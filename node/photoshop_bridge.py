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

# Global registry for Photoshop connections
PHOTOSHOP_CLIENTS = set()
PS_RESPONSES = {}  # request_id -> (asyncio.Event, data)

class PhotoshopSendNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "layer_name": ("STRING", {"default": "ComfyUI_Layer"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("success",)
    FUNCTION = "send"
    CATEGORY = "API/Photoshop"

    def send(self, image, layer_name):
        if not PHOTOSHOP_CLIENTS:
            return (False,)

        # Convert torch image to base64
        img_np = 255. * image[0].cpu().numpy()
        img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        payload = {
            "type": "new_layer",
            "image": img_b64,
            "layer_name": layer_name
        }
        
        message = json.dumps(payload)
        loop = server.PromptServer.instance.loop
        for ws in list(PHOTOSHOP_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))
        
        return (True,)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except:
            PHOTOSHOP_CLIENTS.discard(ws)

class PhotoshopGetNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": True}),
                "timeout": ("INT", {"default": 30, "min": 5, "max": 120}),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN")
    RETURN_NAMES = ("image", "success")
    FUNCTION = "get"
    CATEGORY = "API/Photoshop"

    def get(self, trigger, timeout):
        if not PHOTOSHOP_CLIENTS:
            return (torch.zeros((1, 512, 512, 3)), False)

        request_id = str(uuid.uuid4())
        event = asyncio.Event()
        PS_RESPONSES[request_id] = (event, None)

        payload = {"type": "get_canvas", "request_id": request_id}
        message = json.dumps(payload)
        
        loop = server.PromptServer.instance.loop
        for ws in list(PHOTOSHOP_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if event.is_set():
                _, data = PS_RESPONSES.pop(request_id)
                img_b64 = data.get("image")
                if img_b64:
                    img_data = base64.b64decode(img_b64)
                    img = Image.open(io.BytesIO(img_data)).convert("RGB")
                    img_np = np.array(img).astype(np.float32) / 255.0
                    return (torch.from_numpy(img_np)[None,], True)
            time.sleep(0.2)

        PS_RESPONSES.pop(request_id, None)
        return (torch.zeros((1, 512, 512, 3)), False)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except:
            PHOTOSHOP_CLIENTS.discard(ws)

class PhotoshopStatusNode:
    @classmethod
    def INPUT_TYPES(s): return {"required": {}}
    RETURN_TYPES = ("BOOLEAN", "INT", "STRING")
    RETURN_NAMES = ("is_connected", "active_clients", "status_text")
    FUNCTION = "get_status"
    CATEGORY = "API/Photoshop"

    def get_status(self):
        count = len(PHOTOSHOP_CLIENTS)
        return (count > 0, count, f"Connected clients: {count}" if count > 0 else "Offline")

class PhotoshopGetSelectionNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": True}),
                "timeout": ("INT", {"default": 30, "min": 5, "max": 120}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("image", "mask", "success")
    FUNCTION = "get_selection"
    CATEGORY = "API/Photoshop"

    def get_selection(self, trigger, timeout):
        if not PHOTOSHOP_CLIENTS:
            return (torch.zeros((1, 512, 512, 3)), torch.zeros((1, 512, 512)), False)

        request_id = str(uuid.uuid4())
        event = asyncio.Event()
        PS_RESPONSES[request_id] = (event, None)

        payload = {"type": "get_selection", "request_id": request_id}
        message = json.dumps(payload)
        
        loop = server.PromptServer.instance.loop
        for ws in list(PHOTOSHOP_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if event.is_set():
                _, data = PS_RESPONSES.pop(request_id)
                img_b64 = data.get("image")
                mask_b64 = data.get("mask")
                
                if img_b64:
                    img_data = base64.b64decode(img_b64)
                    img = Image.open(io.BytesIO(img_data)).convert("RGB")
                    img_np = np.array(img).astype(np.float32) / 255.0
                    
                    mask_np = torch.zeros((1, 512, 512))
                    if mask_b64:
                        m_data = base64.b64decode(mask_b64)
                        m_img = Image.open(io.BytesIO(m_data)).convert("L")
                        mask_np = torch.from_numpy(np.array(m_img).astype(np.float32) / 255.0)[None,]

                    return (torch.from_numpy(img_np)[None,], mask_np, True)
            time.sleep(0.2)

        PS_RESPONSES.pop(request_id, None)
        return (torch.zeros((1, 512, 512, 3)), torch.zeros((1, 512, 512)), False)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except: PHOTOSHOP_CLIENTS.discard(ws)

class PhotoshopRunScriptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "script_code": ("STRING", {"multiline": True, "default": "app.activeDocument.activeLayer.invert();"}),
                "trigger": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("success",)
    FUNCTION = "run"
    CATEGORY = "API/Photoshop"

    def run(self, script_code, trigger):
        if not PHOTOSHOP_CLIENTS or not trigger:
            return (False,)

        payload = {"type": "run_jsx", "script": script_code}
        message = json.dumps(payload)
        
        loop = server.PromptServer.instance.loop
        for ws in list(PHOTOSHOP_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))
        
        return (True,)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except: PHOTOSHOP_CLIENTS.discard(ws)

class PhotoshopLayerListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": True}),
                "timeout": ("INT", {"default": 10, "min": 2, "max": 30}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("layers_list", "count", "success")
    FUNCTION = "get_layers"
    CATEGORY = "API/Photoshop"

    def get_layers(self, trigger, timeout):
        if not PHOTOSHOP_CLIENTS:
            return ("", 0, False)

        request_id = str(uuid.uuid4())
        event = asyncio.Event()
        PS_RESPONSES[request_id] = (event, None)

        payload = {"type": "get_layers", "request_id": request_id}
        message = json.dumps(payload)
        
        loop = server.PromptServer.instance.loop
        for ws in list(PHOTOSHOP_CLIENTS):
            loop.call_soon_threadsafe(asyncio.create_task, self.safe_send(ws, message))

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if event.is_set():
                _, data = PS_RESPONSES.pop(request_id)
                layers = data.get("layers", [])
                return (", ".join(layers), len(layers), True)
            time.sleep(0.2)

        PS_RESPONSES.pop(request_id, None)
        return ("", 0, False)

    async def safe_send(self, ws, message):
        try:
            await ws.send_str(message)
        except: PHOTOSHOP_CLIENTS.discard(ws)

async def photoshop_ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    PHOTOSHOP_CLIENTS.add(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")
                    if msg_type in ["canvas_response", "selection_response", "layers_response"]:
                        request_id = data.get("request_id")
                        if request_id in PS_RESPONSES:
                            event, _ = PS_RESPONSES[request_id]
                            PS_RESPONSES[request_id] = (event, data)
                            event.set()
                except Exception as e:
                    print(f"PS Bridge WS Error: {e}")
    finally:
        PHOTOSHOP_CLIENTS.discard(ws)
    return ws

if hasattr(server.PromptServer, "instance"):
    server.PromptServer.instance.app.router.add_get('/api/v1/photoshop/ws', photoshop_ws_handler)

NODE_CLASS_MAPPINGS = {
    "PhotoshopSendNode": PhotoshopSendNode,
    "PhotoshopGetNode": PhotoshopGetNode,
    "PhotoshopStatusNode": PhotoshopStatusNode,
    "PhotoshopGetSelectionNode": PhotoshopGetSelectionNode,
    "PhotoshopRunScriptNode": PhotoshopRunScriptNode,
    "PhotoshopLayerListNode": PhotoshopLayerListNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PhotoshopSendNode": "Send to Photoshop",
    "PhotoshopGetNode": "Get from Photoshop (Full Canvas)",
    "PhotoshopStatusNode": "Photoshop Connection Status",
    "PhotoshopGetSelectionNode": "Get from Photoshop (Selection/Mask)",
    "PhotoshopRunScriptNode": "Photoshop Run JSX Script",
    "PhotoshopLayerListNode": "Photoshop List Layers"
}
