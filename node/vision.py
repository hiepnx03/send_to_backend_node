import torch
import numpy as np
from PIL import Image
import os
import random
import json

# For ImageToText
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
except ImportError:
    BlipProcessor = None
    BlipForConditionalGeneration = None

class ImageToText:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model_name": (["Salesforce/blip-image-captioning-base", "Salesforce/blip-image-captioning-large"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("caption",)
    FUNCTION = "caption_image"
    CATEGORY = "Vision"

    def caption_image(self, image, model_name):
        if BlipProcessor is None:
            return ("Error: 'transformers' library not installed. Please restart ComfyUI to install dependencies.",)

        if self.model is None:
            print(f"Loading vision model: {model_name} (this may take a while)...")
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)

        # Process first image in batch
        i = (255. * image[0].cpu().numpy()).clip(0, 255).astype(np.uint8)
        pil_image = Image.fromarray(i).convert("RGB")

        inputs = self.processor(pil_image, return_tensors="pt").to(self.device)
        out = self.model.generate(**inputs, max_new_tokens=50)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        
        return (caption,)

class PromptAugmenter:
    ANGLES = [
        "low angle", "high angle", "eye level", "overhead shot", 
        "birds eye view", "side view", "close up", "full body shot", 
        "wide angle shot", "extreme close up", "dutch angle"
    ]
    STYLES = [
        "cinematic", "photorealistic", "cyberpunk", "vaporwave", 
        "anime style", "oil painting", "digital art", "minimalist", 
        "gothic", "futuristic", "steampunk", "watercolor", "charcoal sketch"
    ]
    LIGHTING = [
        "soft lighting", "dramatic lighting", "golden hour", 
        "neon lights", "studio lighting", "natural light", 
        "volumetric lighting", "rim lighting", "backlit", "moody lighting"
    ]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "n_variations": ("INT", {"default": 3, "min": 1, "max": 20, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "use_angles": ("BOOLEAN", {"default": True}),
                "use_styles": ("BOOLEAN", {"default": True}),
                "use_lighting": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("combined_text", "first_variation")
    FUNCTION = "augment"
    CATEGORY = "Vision"

    def augment(self, base_prompt, n_variations, seed, use_angles=True, use_styles=True, use_lighting=True):
        random.seed(seed)
        results = []
        for _ in range(n_variations):
            mods = []
            if use_angles: mods.append(random.choice(self.ANGLES))
            if use_styles: mods.append(random.choice(self.STYLES))
            if use_lighting: mods.append(random.choice(self.LIGHTING))
            
            # Combine modifiers and base prompt
            variation = f"{base_prompt}, {', '.join(mods)}"
            results.append(variation)
        
        combined = "\n---\n".join(results)
        first = results[0] if results else base_prompt
        
        return (combined, first)

NODE_CLASS_MAPPINGS = {
    "ImageToText": ImageToText,
    "PromptAugmenter": PromptAugmenter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToText": "AI Image to Prompt (BLIP)",
    "PromptAugmenter": "Creative Prompt Variation (N)"
}
