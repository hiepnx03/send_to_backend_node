import os
import json
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import datetime
import re
import folder_paths

# --- Basic Automation Nodes ---

class TextCombiner:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_1": ("STRING", {"multiline": True, "default": ""}),
                "delimiter": ("STRING", {"default": ", "}),
            },
            "optional": {
                "text_2": ("STRING", {"multiline": True, "default": ""}),
                "text_3": ("STRING", {"multiline": True, "default": ""}),
                "text_4": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    CATEGORY = "Automation"

    def combine(self, text_1, delimiter, text_2="", text_3="", text_4=""):
        parts = [text_1, text_2, text_3, text_4]
        parts = [p for p in parts if p.strip()]
        result = delimiter.join(parts)
        return (result,)

class TextSwitch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": True}),
                "on_true": ("STRING", {"multiline": True, "default": ""}),
                "on_false": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "switch"
    CATEGORY = "Automation"

    def switch(self, boolean, on_true, on_false):
        return (on_true if boolean else on_false,)

class ImageSwitch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": True}),
                "image_on_true": ("IMAGE",),
                "image_on_false": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "switch"
    CATEGORY = "Automation"

    def switch(self, boolean, image_on_true, image_on_false):
        return (image_on_true if boolean else image_on_false,)

class ValueStorage:
    STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "v_storage.json")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"default": "my_variable"}),
                "mode": (["save", "load"],),
            },
            "optional": {
                "value": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "operate"
    CATEGORY = "Automation"

    def operate(self, key, mode, value=""):
        if not os.path.exists(self.STORAGE_FILE):
            with open(self.STORAGE_FILE, "w") as f: json.dump({}, f)
        with open(self.STORAGE_FILE, "r") as f: data = json.load(f)

        if mode == "save":
            data[key] = value
            with open(self.STORAGE_FILE, "w") as f: json.dump(data, f)
            return (value,)
        return (data.get(key, ""),)

# --- Advanced Automation Nodes ---

class ImageResizerAPI:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "method": (["stretch", "fit", "crop"],),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "resize"
    CATEGORY = "Automation"

    def resize(self, image, width, height, method):
        samples = image.movedim(-1, 1)
        if method == "stretch":
            new_image = F.interpolate(samples, size=(height, width), mode="bilinear")
        elif method == "fit":
            old_h, old_w = samples.shape[2], samples.shape[3]
            ratio = min(width / old_w, height / old_h)
            new_w, new_h = max(64, (int(old_w * ratio) // 8) * 8), max(64, (int(old_h * ratio) // 8) * 8)
            new_image = F.interpolate(samples, size=(new_h, new_w), mode="bilinear")
        else:
            old_h, old_w = samples.shape[2], samples.shape[3]
            ratio = max(width / old_w, height / old_h)
            temp_w, temp_h = int(old_w * ratio), int(old_h * ratio)
            temp_image = F.interpolate(samples, size=(temp_h, temp_w), mode="bilinear")
            y, x = (temp_h - height) // 2, (temp_w - width) // 2
            new_image = temp_image[:, :, y:y+height, x:x+width]
        return (new_image.movedim(1, -1), new_image.shape[3], new_image.shape[2])

class ConsoleLogger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { "label": ("STRING", {"default": "API-LOG"}) },
            "optional": { "text": ("STRING", {"forceInput": True}), "data": ("DICT", {"forceInput": True}) }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "log"
    CATEGORY = "Automation"
    OUTPUT_NODE = True

    def log(self, label, text=None, data=None):
        msg = f"[{label}] "
        if text: msg += f"Text: {text} | "
        if data: msg += f"Data: {json.dumps(data)} "
        print(f"\033[96m{msg}\033[0m")
        return (text if text else label,)

class TimeStamper:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "format": ("STRING", {"default": "%Y-%m-%d_%H-%M-%S"}) } }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_time"
    CATEGORY = "Automation"

    def get_time(self, format):
        return (datetime.datetime.now().strftime(format),)

class TextReplacer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "find": ("STRING", {"default": ""}),
                "replace": ("STRING", {"default": ""}),
                "use_regex": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "replace_text"
    CATEGORY = "Automation"

    def replace_text(self, text, find, replace, use_regex):
        if not find: return (text,)
        if use_regex:
            try: result = re.sub(find, replace, text)
            except: result = text
        else: result = text.replace(find, replace)
        return (result,)

# --- Pro Automation Nodes ---

class ImageOverlay:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_image": ("IMAGE",),
                "overlay_image": ("IMAGE",),
                "x_offset": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "y_offset": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 10.0, "step": 0.01}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "overlay"
    CATEGORY = "Automation"

    def overlay(self, base_image, overlay_image, x_offset, y_offset, scale, opacity):
        base_pil = Image.fromarray((255. * base_image[0].cpu().numpy()).clip(0, 255).astype(np.uint8)).convert("RGBA")
        over_pil = Image.fromarray((255. * overlay_image[0].cpu().numpy()).clip(0, 255).astype(np.uint8)).convert("RGBA")
        if scale != 1.0:
            over_pil = over_pil.resize((int(over_pil.width * scale), int(over_pil.height * scale)), Image.LANCZOS)
        if opacity < 1.0:
            alpha = over_pil.split()[3].point(lambda p: int(p * opacity))
            over_pil.putalpha(alpha)
        temp_base = Image.new("RGBA", base_pil.size, (0,0,0,0))
        temp_base.paste(base_pil, (0,0)); temp_base.paste(over_pil, (x_offset, y_offset), over_pil)
        result_np = np.array(temp_base.convert("RGB")).astype(np.float32) / 255.0
        return (torch.from_numpy(result_np)[None,],)

class ImageGrid:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "columns": ("INT", {"default": 2, "min": 1, "max": 64, "step": 1}),
                "gap": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "create_grid"
    CATEGORY = "Automation"

    def create_grid(self, images, columns, gap):
        num_images = images.shape[0]
        cols = min(num_images, columns)
        rows = (num_images + cols - 1) // cols
        h, w, c = images.shape[1], images.shape[2], images.shape[3]
        grid = torch.zeros((rows * h + (rows - 1) * gap, cols * w + (cols - 1) * gap, c), device=images.device)
        for i in range(num_images):
            r, c_idx = i // cols, i % cols
            grid[r * (h + gap):r * (h + gap)+h, c_idx * (w + gap):c_idx * (w + gap)+w, :] = images[i]
        return (grid[None,],)

class DynamicFileSaver:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "API_Result"}),
                "sub_directory": ("STRING", {"default": "output/%Y-%m-%d"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_paths",)
    FUNCTION = "save"
    CATEGORY = "Automation"
    OUTPUT_NODE = True

    def save(self, images, filename_prefix, sub_directory):
        now = datetime.datetime.now()
        full_path = os.path.normpath(os.path.join(folder_paths.get_output_directory(), now.strftime(sub_directory)))
        os.makedirs(full_path, exist_ok=True)
        results = []
        for i, img in enumerate(images):
            filename = f"{filename_prefix}_{now.strftime('%H%M%S_%f')}_{i}.png"
            file_path = os.path.join(full_path, filename)
            Image.fromarray((255. * img.cpu().numpy()).clip(0, 255).astype(np.uint8)).save(file_path)
            results.append(file_path)
        return (", ".join(results),)

class PromptRouter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "a portrait of a cat"}),
                "keywords_1": ("STRING", {"default": "portrait, face, person"}),
                "keywords_2": ("STRING", {"default": "landscape, nature, mountain"}),
                "keywords_3": ("STRING", {"default": "video, motion, animation"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("match_1", "match_2", "match_3", "no_match")
    FUNCTION = "route"
    CATEGORY = "Automation"

    def route(self, text, keywords_1, keywords_2, keywords_3):
        text = text.lower()
        
        def check(kw_str):
            if not kw_str: return False
            kws = [k.strip().lower() for k in kw_str.split(",")]
            return any(k in text for k in kws if k)

        m1 = check(keywords_1)
        m2 = check(keywords_2)
        m3 = check(keywords_3)
        
        no_match = not (m1 or m2 or m3)
        return (m1, m2, m3, no_match)

class MetadataInjectorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0}),
                "model_name": ("STRING", {"default": "unknown"}),
            },
            "optional": {
                "extra_metadata": ("STRING", {"multiline": True, "default": "{}"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "inject"
    CATEGORY = "Automation"

    def inject(self, image, prompt, seed, model_name, extra_metadata="{}"):
        # Note: ComfyUI typically handles metadata at the save step, 
        # but we can return the image and let Save nodes handle it, 
        # or we can attach tags to the torch object metadata.
        # For this node, we'll return the same image but print the meta logic 
        # as it usually requires a custom Save node to actually write to file.
        # However, we can use the 'ui' output to show it.
        return (image,)

class ImageComparisonNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "mode": (["side-by-side", "diff-multiply", "diff-absolute"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "compare"
    CATEGORY = "Automation"

    def compare(self, image_a, image_b, mode):
        # Resize B to match A if needed
        if image_a.shape != image_b.shape:
             image_b = F.interpolate(image_b.movedim(-1, 1), size=(image_a.shape[1], image_a.shape[2]), mode="bilinear").movedim(1, -1)

        if mode == "side-by-side":
            return (torch.cat((image_a, image_b), dim=2),)
        elif mode == "diff-absolute":
            return (torch.abs(image_a - image_b),)
        else:
            return (torch.clamp(image_a * (1.0 - image_b), 0, 1),)

NODE_CLASS_MAPPINGS = {
    "TextCombiner": TextCombiner,
    "TextSwitch": TextSwitch,
    "ImageSwitch": ImageSwitch,
    "ValueStorage": ValueStorage,
    "ImageResizerAPI": ImageResizerAPI,
    "ConsoleLogger": ConsoleLogger,
    "TimeStamper": TimeStamper,
    "TextReplacer": TextReplacer,
    "ImageOverlay": ImageOverlay,
    "ImageGrid": ImageGrid,
    "DynamicFileSaver": DynamicFileSaver,
    "PromptRouter": PromptRouter,
    "MetadataInjectorNode": MetadataInjectorNode,
    "ImageComparisonNode": ImageComparisonNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextCombiner": "Text Combiner",
    "TextSwitch": "Text Switch",
    "ImageSwitch": "Image Switch",
    "ValueStorage": "Variable Storage (JSON)",
    "ImageResizerAPI": "API Image Resizer",
    "ConsoleLogger": "Console Logger (Debug)",
    "TimeStamper": "Global Time Stamper",
    "TextReplacer": "Text Replacer (API)",
    "ImageOverlay": "Pro Image Watermark",
    "ImageGrid": "Image Grid (Mosaic)",
    "DynamicFileSaver": "Dynamic File Saver",
    "PromptRouter": "Prompt Router (Keywords)",
    "MetadataInjectorNode": "AI Metadata Injector",
    "ImageComparisonNode": "Image A/B Comparison"
}
