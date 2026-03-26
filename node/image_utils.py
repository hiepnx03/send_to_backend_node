import torch
import numpy as np
from PIL import Image
import io
import base64
from sklearn.cluster import KMeans

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

class ColorPaletteExtractor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_colors": ("INT", {"default": 5, "min": 1, "max": 10}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("hex_list", "json_palette")
    FUNCTION = "extract"
    CATEGORY = "API/ImageUtils"

    def extract(self, image, num_colors):
        # image is [batch, h, w, c]
        img_np = 255. * image[0].cpu().numpy()
        img_np = img_np.astype(np.uint8)
        
        # Resize for faster clustering
        img = Image.fromarray(img_np)
        img.thumbnail((100, 100))
        pixels = np.array(img).reshape(-1, 3)
        
        # KMeans to find dominant colors
        kmeans = KMeans(n_clusters=num_colors, n_init=10)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int)
        
        hex_colors = []
        for c in colors:
            hex_colors.append('#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]))
            
        import json
        return (", ".join(hex_colors), json.dumps(hex_colors))

class AutoBackgroundRemover:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "remove_bg"
    CATEGORY = "API/ImageUtils"

    def remove_bg(self, image):
        if not REMBG_AVAILABLE:
            print("⚠️ rembg not installed. Background removal skipped.")
            return (image, torch.zeros_like(image[:,:,:,0]))

        # image is [batch, h, w, c]
        img_np = 255. * image[0].cpu().numpy()
        img_pil = Image.fromarray(img_np.astype(np.uint8))
        
        # Remove background
        result_pil = remove(img_pil)
        
        # Split RGBA
        if result_pil.mode == 'RGBA':
            r, g, b, a = result_pil.split()
            result_rgb = Image.merge('RGB', (r, g, b))
            
            mask_np = np.array(a).astype(np.float32) / 255.0
            image_np = np.array(result_rgb).astype(np.float32) / 255.0
            
            return (torch.from_numpy(image_np)[None,], torch.from_numpy(mask_np)[None,])
        
        return (image, torch.zeros_like(image[:,:,:,0]))

NODE_CLASS_MAPPINGS = {
    "ColorPaletteExtractor": ColorPaletteExtractor,
    "AutoBackgroundRemover": AutoBackgroundRemover
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorPaletteExtractor": "Color Palette Extractor",
    "AutoBackgroundRemover": "Auto Background Remover (Rembg)"
}
