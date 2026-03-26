import torch
import numpy as np
from PIL import Image

class VideoPreviewNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "frame_count": ("INT", {"default": 4, "min": 2, "max": 16}),
                "columns": ("INT", {"default": 2, "min": 1, "max": 4}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("grid_image",)
    FUNCTION = "create_preview"
    CATEGORY = "API/VideoUtils"

    def create_preview(self, images, frame_count, columns):
        # images is [batch, h, w, c]
        total_frames = images.shape[0]
        
        # Pick frames evenly
        indices = np.linspace(0, total_frames - 1, frame_count).astype(int)
        selected_frames = images[indices]
        
        # Create grid
        batch, height, width, channels = selected_frames.shape
        rows = (batch + columns - 1) // columns
        
        grid = torch.zeros((rows * height, columns * width, channels))
        
        for i in range(batch):
            r = i // columns
            c = i % columns
            grid[r*height:(r+1)*height, c*width:(c+1)*width, :] = selected_frames[i]
            
        return (grid.unsqueeze(0),)

NODE_CLASS_MAPPINGS = {
    "VideoPreviewNode": VideoPreviewNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoPreviewNode": "Video Preview (Frame Grid)"
}
