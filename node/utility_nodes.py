import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math
import uuid
import random

class MathExpressionNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "expression": ("STRING", {"default": "(a + b) / 2"}),
                "a": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "b": ("FLOAT", {"default": 0.0, "step": 0.01}),
            },
            "optional": {
                "c": ("FLOAT", {"default": 0.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("float_val", "int_val", "string_val")
    FUNCTION = "evaluate"
    CATEGORY = "API/Utility"

    def evaluate(self, expression, a, b, c=0.0):
        # Safe eval using math functions
        safe_dict = {
            "a": a, "b": b, "c": c,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "abs": abs, "round": round, "min": min, "max": max
        }
        try:
            result = float(eval(expression, {"__builtins__": None}, safe_dict))
            return (result, int(result), str(result))
        except Exception as e:
            print(f"Math Error: {e}")
            return (0.0, 0, f"Error: {e}")

class AdvancedTextOverlayNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"multiline": True, "default": "Hello World"}),
                "font_size": ("INT", {"default": 40, "min": 10, "max": 500}),
                "x_margin": ("FLOAT", {"default": 0.05, "min": 0, "max": 1, "step": 0.01}),
                "y_margin": ("FLOAT", {"default": 0.05, "min": 0, "max": 1, "step": 0.01}),
                "alignment": (["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"],),
                "color": ("STRING", {"default": "#FFFFFF"}),
            },
            "optional": {
                "shadow_color": ("STRING", {"default": "#000000"}),
                "shadow_offset": ("INT", {"default": 2}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "overlay"
    CATEGORY = "API/Utility"

    def overlay(self, image, text, font_size, x_margin, y_margin, alignment, color, shadow_color="#000000", shadow_offset=2):
        img_np = 255. * image[0].cpu().numpy()
        pil_img = Image.fromarray(img_np.astype(np.uint8)).convert("RGBA")
        draw = ImageDraw.Draw(pil_img)
        
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        w, h = pil_img.size
        # Get multiline text size
        text_w, text_h = draw.multiline_textsize(text, font=font) if hasattr(draw, "multiline_textsize") else (font_size * len(text) * 0.5, font_size)

        x, y = 0, 0
        mx, my = int(w * x_margin), int(h * y_margin)

        if "left" in alignment: x = mx
        elif "right" in alignment: x = w - text_w - mx
        else: x = (w - text_w) // 2

        if "top" in alignment: y = my
        elif "bottom" in alignment: y = h - text_h - my
        else: y = (h - text_h) // 2
        
        if alignment == "center":
            x, y = (w - text_w) // 2, (h - text_h) // 2

        # Draw Shadow
        if shadow_offset > 0:
            draw.multiline_text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Draw Text
        draw.multiline_text((x, y), text, font=font, fill=color)
        
        res_np = np.array(pil_img.convert("RGB")).astype(np.float32) / 255.0
        return (torch.from_numpy(res_np)[None,],)

class ImageSharpenerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "sharpen"
    CATEGORY = "API/Utility"

    def sharpen(self, image, strength):
        img_np = 255. * image[0].cpu().numpy()
        pil_img = Image.fromarray(img_np.astype(np.uint8))
        
        # Apply sharpen filter multiple times based on strength
        res = pil_img
        for _ in range(int(strength)):
             res = res.filter(ImageFilter.SHARPEN)
        
        # Handle fractional strength
        if strength % 1 > 0:
            sharper = res.filter(ImageFilter.SHARPEN)
            res = Image.blend(res, sharper, strength % 1)

        res_np = np.array(res).astype(np.float32) / 255.0
        return (torch.from_numpy(res_np)[None,],)

class AutoCropNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:5", "2:3", "3:2"],),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "crop"
    CATEGORY = "API/Utility"

    def crop(self, image, aspect_ratio):
        img_np = 255. * image[0].cpu().numpy()
        pil_img = Image.fromarray(img_np.astype(np.uint8))
        
        r_map = {"1:1": (1,1), "16:9": (16,9), "9:16": (9,16), "4:5": (4,5), "2:3": (2,3), "3:2": (3,2)}
        rw, rh = r_map[aspect_ratio]
        
        # Calculate target size keeping best fit
        curr_w, curr_h = pil_img.size
        # Use ImageOps.fit to crop to aspect ratio
        res = ImageOps.fit(pil_img, (curr_w, int(curr_w * rh / rw)) if curr_w/curr_h > rw/rh else (int(curr_h * rw / rh), curr_h))
        
        res_np = np.array(res).astype(np.float32) / 255.0
        return (torch.from_numpy(res_np)[None,], res.width, res.height)

class RandomGeneratorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["uuid", "filename", "hex_color", "int_range"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "prefix": ("STRING", {"default": "file_"}),
                "min_val": ("INT", {"default": 0}),
                "max_val": ("INT", {"default": 100}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("string_val", "int_val")
    FUNCTION = "generate"
    CATEGORY = "API/Utility"

    def generate(self, mode, seed, prefix="file_", min_val=0, max_val=100):
        random.seed(seed)
        if mode == "uuid":
            val = str(uuid.uuid4())
            return (val, 0)
        elif mode == "filename":
            val = f"{prefix}{int(time.time())}_{random.randint(1000, 9999)}"
            import time # Local import to be sure
            return (val, 0)
        elif mode == "hex_color":
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            return (color, int(color[1:], 16))
        else:
            val = random.randint(min_val, max_val)
            return (str(val), val)

NODE_CLASS_MAPPINGS = {
    "MathExpressionNode": MathExpressionNode,
    "AdvancedTextOverlayNode": AdvancedTextOverlayNode,
    "ImageSharpenerNode": ImageSharpenerNode,
    "AutoCropNode": AutoCropNode,
    "RandomGeneratorNode": RandomGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MathExpressionNode": "Ultimate Math Expression",
    "AdvancedTextOverlayNode": "Advanced Text Overlay",
    "ImageSharpenerNode": "Professional Image Sharpener",
    "AutoCropNode": "Smart Auto-Crop (Aspect Ratio)",
    "RandomGeneratorNode": "Ultimate Random Generator"
}
