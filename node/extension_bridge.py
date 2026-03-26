import server
import asyncio
import json
import uuid
import time
import io
import base64
import numpy as np
from PIL import Image
from aiohttp import web
import torch

# Global registry for extension connections
EXTENSION_CLIENTS = set()
LATEST_RESPONSES = {}  # prompt_id -> (asyncio.Event, data)

class GeminiExtensionNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Describe this image"}),
                "model": (["Gemini 2.0 Flash", "Gemini 1.5 Pro", "Gemini 1.5 Flash"], {"default": "Gemini 2.0 Flash"}),
                "timeout": ("INT", {"default": 60, "min": 10, "max": 300}),
            },
            "optional": {
                "image": ("IMAGE",),
                "history": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("response_text", "updated_history", "success")
    FUNCTION = "interact"
    CATEGORY = "API/Extension"

    def interact(self, prompt, model, timeout, image=None, history=""):
        if not EXTENSION_CLIENTS:
            return ("Error: No browser extension connected.", history, False)

        prompt_id = str(uuid.uuid4())
        event = asyncio.Event()
        LATEST_RESPONSES[prompt_id] = (event, None)

        payload = {
            "type": "gemini_request",
            "prompt_id": prompt_id,
            "prompt": prompt,
            "model": model,
            "history": history
        }

        if image is not None:
            img_np = 255. * image[0].cpu().numpy()
            img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            payload["image_base64"] = base64.b64encode(buffered.getvalue()).decode("utf-8")

        message = json.dumps(payload)
        loop = server.PromptServer.instance.loop
        for ws in list(EXTENSION_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))

        start_time = time.time()
        while time.time() - start_time < timeout:
            if event.is_set():
                _, data = LATEST_RESPONSES.pop(prompt_id)
                res_text = data.get("text", "No text returned")
                new_history = history + f"\nUser: {prompt}\nGemini: {res_text}\n"
                return (res_text, new_history, True)
            time.sleep(0.5)

        LATEST_RESPONSES.pop(prompt_id, None)
        return ("Error: Request timed out.", history, False)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except:
            EXTENSION_CLIENTS.discard(ws)

async def extension_ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    EXTENSION_CLIENTS.add(ws)
    print(f"Browser Extension Bridge: Extension connected. Total: {len(EXTENSION_CLIENTS)}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    if data.get("type") == "gemini_response":
                        prompt_id = data.get("prompt_id")
                        if prompt_id in LATEST_RESPONSES:
                            event, _ = LATEST_RESPONSES[prompt_id]
                            LATEST_RESPONSES[prompt_id] = (event, data)
                            event.set()
                except Exception as e:
                    print(f"Extension Bridge Error: {e}")
            elif msg.type == web.WSMsgType.ERROR:
                print(f"Extension Bridge WS error: {ws.exception()}")
    finally:
        EXTENSION_CLIENTS.discard(ws)
        print(f"Browser Extension Bridge: Extension disconnected. Total: {len(EXTENSION_CLIENTS)}")

    return ws

# Register the route
if hasattr(server.PromptServer, "instance"):
    server.PromptServer.instance.app.router.add_get('/api/v1/extension/ws', extension_ws_handler)

NODE_CLASS_MAPPINGS = {
    "GeminiExtensionNode": GeminiExtensionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiExtensionNode": "Gemini Browser Bridge"
}