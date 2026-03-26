import os
import json
import uuid
import server
from aiohttp import web
import folder_paths
import execution
import torch
import numpy as np
from PIL import Image
import asyncio
import io
import base64
import requests
import time

# Workflows storage directory
WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")
os.makedirs(WORKFLOWS_DIR, exist_ok=True)

# For Synchronous API Response
RESPONSE_REGISTRY = {}      # prompt_id -> asyncio.Event
RESULT_DATA = {}            # prompt_id -> dict
EXECUTION_START_TIMES = {}   # prompt_id -> timestamp

class APITrigger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "workflow_name": ("STRING", {"default": "default"}),
                "api_data": ("STRING", {"multiline": True, "default": "{}"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "DICT", "INT")
    RETURN_NAMES = ("first_image", "first_text", "all_data", "batch_size")
    FUNCTION = "execute"
    CATEGORY = "API"

    def execute(self, workflow_name, api_data, batch_size):
        try:
            data = json.loads(api_data)
        except:
            data = {}

        first_image = torch.zeros((1, 64, 64, 3))
        first_text = ""

        # Find first image and first text
        for key, value in data.items():
            if isinstance(value, str):
                if not first_text and not value.startswith(folder_paths.get_input_directory()):
                    first_text = value
                
                # Check if it's a saved prompt image path
                if value.endswith((".png", ".jpg", ".jpeg", ".webp")) and os.path.exists(value):
                    try:
                        img = Image.open(value).convert("RGB")
                        first_image = np.array(img).astype(np.float32) / 255.0
                        first_image = torch.from_numpy(first_image)[None,]
                    except:
                        pass
        
        return (first_image, first_text, data, batch_size)

class GetFromAPI:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "all_data": ("DICT",),
                "key": ("STRING", {"default": "text"}),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE")
    FUNCTION = "get_data"
    CATEGORY = "API"

    def get_data(self, all_data, key):
        value = all_data.get(key, "")
        image = torch.zeros((1, 64, 64, 3))
        text = str(value)

        if isinstance(value, str) and value.endswith((".png", ".jpg", ".jpeg", ".webp")) and os.path.exists(value):
            try:
                img = Image.open(value).convert("RGB")
                image = np.array(img).astype(np.float32) / 255.0
                image = torch.from_numpy(image)[None,]
            except:
                pass
        
        return (text, image)

class ApiResponse:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt_id": ("STRING", {"default": ""}),
                "include_image": ("BOOLEAN", {"default": True}),
                "include_text": ("BOOLEAN", {"default": True}),
                "include_stats": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "image": ("IMAGE",),
                "text": ("STRING", {"default": ""}),
                "extra_data": ("DICT", {"default": {}}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "send_response"
    CATEGORY = "API"
    OUTPUT_NODE = True

    def send_response(self, prompt_id, include_image, include_text, include_stats, image=None, text="", extra_data={}):
        if not prompt_id:
            return ("No prompt_id provided",)

        result = {}
        if include_text:
            result["text"] = text
        
        if include_image and image is not None:
            if image.shape[0] > 1:
                img_list = []
                for i in range(image.shape[0]):
                    img_np = 255. * image[i].cpu().numpy()
                    img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_list.append(base64.b64encode(buffered.getvalue()).decode("utf-8"))
                result["images_base64"] = img_list
            else:
                img_np = 255. * image[0].cpu().numpy()
                img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                result["image_base64"] = base64.b64encode(buffered.getvalue()).decode("utf-8")

        if include_stats:
            start_time = EXECUTION_START_TIMES.get(prompt_id, time.time())
            execution_time = round(time.time() - start_time, 2)
            result["stats"] = {
                "execution_time_sec": execution_time,
                "batch_size": image.shape[0] if image is not None else 0,
                "resolution": f"{image.shape[2]}x{image.shape[1]}" if image is not None else "N/A"
            }
        
        if extra_data:
            result[ "extra" ] = extra_data

        RESULT_DATA[prompt_id] = result
        if prompt_id in RESPONSE_REGISTRY:
            event = RESPONSE_REGISTRY[prompt_id]
            server.PromptServer.instance.loop.call_soon_threadsafe(event.set)
        
        # Cleanup timing storage
        EXECUTION_START_TIMES.pop(prompt_id, None)
        
        return ("Response prepared",)

def register_workflow_handler(json_data):
    try:
        prompt = json_data.get("prompt", {})
        for node_id in prompt:
            node = prompt[node_id]
            if node.get("class_type") == "APITrigger":
                workflow_name = node["inputs"].get("workflow_name", "default")
                filepath = os.path.join(WORKFLOWS_DIR, f"{workflow_name}.json")
                with open(filepath, "w") as f:
                    json.dump(json_data, f)
                print(f"Registered workflow '{workflow_name}' for API triggering.")
                # We can have multiple trigger nodes but usually one per workflow is enough
    except Exception as e:
        print(f"Error registering workflow: {e}")
    
    return json_data

if hasattr(server.PromptServer, "instance"):
    server.PromptServer.instance.add_on_prompt_handler(register_workflow_handler)

    @server.PromptServer.instance.routes.get("/api/v1/workflows")
    async def api_list_workflows(request):
        files = [f[:-5] for f in os.listdir(WORKFLOWS_DIR) if f.endswith(".json")]
        return web.json_response({"workflows": files})

    @server.PromptServer.instance.routes.post("/api/v1/trigger")
    async def api_v1_trigger(request):
        try:
            post = await request.post()
            wait_for_result = request.rel_url.query.get("wait", "false").lower() == "true"
            workflow_name = request.rel_url.query.get("workflow", post.get("workflow", "default"))
            
            batch_count = 1
            try:
                if "batch" in post: batch_count = int(post.get("batch", 1))
            except: pass
            
            api_data_dict = {}
            upload_dir = os.path.join(folder_paths.get_input_directory(), "api_trigger")
            os.makedirs(upload_dir, exist_ok=True)

            has_image = False; has_text = False

            for key in post:
                if key in ["batch", "workflow"]: continue
                value = post[key]
                if isinstance(value, web.FileField):
                    filename = f"{uuid.uuid4()}_{value.filename}"
                    filepath = os.path.normpath(os.path.join(upload_dir, filename))
                    with open(filepath, "wb") as f: f.write(value.file.read())
                    api_data_dict[key] = filepath; has_image = True
                else:
                    if isinstance(value, str) and value.startswith(("http://", "https://")):
                        try:
                            response = requests.get(value, timeout=10)
                            if response.status_code == 200:
                                ext = ".png"
                                if "content-type" in response.headers:
                                    ct = response.headers["content-type"].lower()
                                    if "jpeg" in ct: ext = ".jpg"; 
                                    elif "webp" in ct: ext = ".webp"
                                filename = f"{uuid.uuid4()}{ext}"
                                filepath = os.path.normpath(os.path.join(upload_dir, filename))
                                with open(filepath, "wb") as f: f.write(response.content)
                                api_data_dict[key] = filepath
                                has_image = True
                            else:
                                api_data_dict[key] = value
                                if value.strip():
                                    has_text = True
                        except:
                            api_data_dict[key] = value
                            if value.strip():
                                has_text = True
                    else:
                        api_data_dict[key] = value
                        if isinstance(value, str) and value.strip():
                            has_text = True

            if not (has_image or has_text):
                return web.json_response({"error": "Bắt buộc phải có ít nhất 1 ảnh (file/URL) hoặc text."}, status=400)

            wf_path = os.path.join(WORKFLOWS_DIR, f"{workflow_name}.json")
            if not os.path.exists(wf_path):
                return web.json_response({"error": f"Workflow '{workflow_name}' chưa được đăng ký. Vui lòng đặt tên workflow trong node APITrigger và nhấn Queue một lần."}, status=400)

            with open(wf_path, "r") as f:
                workflow_data = json.load(f)

            prompt = workflow_data.get("prompt", {})
            prompt_id = str(uuid.uuid4())
            EXECUTION_START_TIMES[prompt_id] = time.time()
            
            found_trigger = False
            for node_id in prompt:
                class_type = prompt[node_id].get("class_type")
                if class_type == "APITrigger":
                    prompt[node_id]["inputs"]["api_data"] = json.dumps(api_data_dict)
                    prompt[node_id]["inputs"]["batch_size"] = batch_count; found_trigger = True
                elif class_type == "ApiResponse":
                    prompt[node_id]["inputs"]["prompt_id"] = prompt_id
            
            if not found_trigger:
                 return web.json_response({"error": f"Không tìm thấy node APITrigger trong workflow '{workflow_name}'"}, status=400)

            event = None
            if wait_for_result:
                event = asyncio.Event()
                RESPONSE_REGISTRY[prompt_id] = event

            valid = await execution.validate_prompt(prompt_id, prompt)
            
            if valid[0]:
                outputs_to_execute = valid[2]
                server.PromptServer.instance.loop.call_soon_threadsafe(
                    server.PromptServer.instance.prompt_queue.put,
                    (server.PromptServer.instance.number, prompt_id, prompt, workflow_data.get("extra_data", {}), outputs_to_execute, {})
                )
                server.PromptServer.instance.number += 1
                
                if wait_for_result and event:
                    try:
                        await asyncio.wait_for(event.wait(), timeout=120.0)
                        result = RESULT_DATA.pop(prompt_id, {})
                        return web.json_response({"status": "success", "workflow": workflow_name, "prompt_id": prompt_id, "result": result})
                    except asyncio.TimeoutError:
                        return web.json_response({"status": "timeout", "prompt_id": prompt_id, "message": "Workflow timed out"}, status=504)
                    finally:
                        RESPONSE_REGISTRY.pop(prompt_id, None)
                        EXECUTION_START_TIMES.pop(prompt_id, None)
                
                return web.json_response({"status": "success", "workflow": workflow_name, "prompt_id": prompt_id, "batch": batch_count})
            else:
                if prompt_id in RESPONSE_REGISTRY: RESPONSE_REGISTRY.pop(prompt_id)
                EXECUTION_START_TIMES.pop(prompt_id, None)
                return web.json_response({"error": f"Invalid prompt: {valid[1]}", "node_errors": valid[3]}, status=400)

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

NODE_CLASS_MAPPINGS = {
    "APITrigger": APITrigger,
    "GetFromAPI": GetFromAPI,
    "ApiResponse": ApiResponse
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APITrigger": "API Trigger (Dynamic)",
    "GetFromAPI": "Get Data From API",
    "ApiResponse": "API Response (Sync Out)"
}
