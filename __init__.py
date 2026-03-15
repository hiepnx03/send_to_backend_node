import torch
import numpy as np
from PIL import Image
import requests
import io
import os
import json

class SendToBackend:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "backend_url": ("STRING", {"default": "http://apiprompt.nauan.click"}),
                "category_id": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "workflow_id": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
            },
            "optional": {
                "prompt_text": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    FUNCTION = "send_images"
    CATEGORY = "Backend"

    def send_images(self, images, backend_url, category_id, workflow_id, prompt_text=""):
        results = []
        
        for image in images:
            # Convert torch tensor to PIL image
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Save PIL image to bytes
            byte_io = io.BytesIO()
            img.save(byte_io, format='PNG')
            byte_io.seek(0)
            
            # 1. Upload to /api/upload
            try:
                files = {'files': ('image.png', byte_io, 'image/png')}
                upload_resp = requests.post(f"{backend_url}/api/upload", files=files)
                upload_resp.raise_for_status()
                upload_data = upload_resp.json()
                image_path = upload_data['paths'][0]
                print(f"Uploaded image to: {image_path}")
                
                # 2. Add to /api/prompts/add
                prompt_data = {
                    "prompt": prompt_text,
                    "image": image_path,
                    "categoryId": category_id,
                    "workflowId": workflow_id,
                    "media": [image_path]
                }
                add_resp = requests.post(f"{backend_url}/api/prompts/add", json=prompt_data)
                add_resp.raise_for_status()
                print(f"Added prompt entry to backend.")
                
            except Exception as e:
                print(f"Error sending to backend: {e}")

        return (images,)

NODE_CLASS_MAPPINGS = {
    "SendToBackend": SendToBackend
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SendToBackend": "Send To Backend ??"
}
