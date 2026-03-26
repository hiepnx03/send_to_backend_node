import requests
import torch
import numpy as np
from PIL import Image
import io
import json

class WebhookNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "webhook_url": ("STRING", {"default": "http://example.com/webhook"}),
            },
            "optional": {
                "images": ("IMAGE",),
                "data": ("DICT",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "send_webhook"
    CATEGORY = "API"
    OUTPUT_NODE = True

    def send_webhook(self, webhook_url, images=None, data=None):
        payload = {}
        if data:
            payload["data"] = json.dumps(data)
        
        files = []
        if images is not None:
            for i, image in enumerate(images):
                # Handle torch tensor [B, H, W, C]
                img_np = 255. * image.cpu().numpy()
                img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
                byte_io = io.BytesIO()
                img.save(byte_io, format='PNG')
                byte_io.seek(0)
                files.append(('files', (f'image_{i}.png', byte_io, 'image/png')))

        try:
            if files:
                resp = requests.post(webhook_url, data=payload, files=files)
            else:
                resp = requests.post(webhook_url, json=payload)
            resp.raise_for_status()
            print(f"Webhook sent successfully to {webhook_url}")
            return (f"Success: {resp.status_code}",)
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return (f"Error: {str(e)}",)

NODE_CLASS_MAPPINGS = {
    "WebhookNode": WebhookNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WebhookNode": "Automated Webhook"
}
