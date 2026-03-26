import server
import torch
import psutil
import json

class StatusNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "dummy_input": ("INT", {"default": 1, "min": 0, "max": 1, "step": 1}),
            }
        }

    RETURN_TYPES = ("DICT", "STRING", "BOOLEAN")
    RETURN_NAMES = ("all_stats", "summary_text", "is_idle")
    FUNCTION = "get_status"
    CATEGORY = "API"

    def get_status(self, dummy_input):
        # 1. Queue Status from ComfyUI
        queue_info = server.PromptServer.instance.prompt_queue.get_current_queue()
        running_count = len(queue_info[0])
        pending_count = len(queue_info[1])
        
        # 2. System Status (CPU, RAM)
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        # 3. GPU Status (VRAM)
        gpu_stats = []
        if torch.cuda.is_available():
            try:
                for i in range(torch.cuda.device_count()):
                    name = torch.cuda.get_device_name(i)
                    free, total = torch.cuda.mem_get_info(i)
                    gpu_stats.append({
                        "device_index": i,
                        "name": name,
                        "vram_free_gb": round(free / (1024**3), 2),
                        "vram_total_gb": round(total / (1024**3), 2),
                        "vram_used_gb": round((total - free) / (1024**3), 2),
                        "vram_percent": round(((total - free) / total) * 100, 1)
                    })
            except Exception as e:
                gpu_stats = [{"error": str(e)}]
        
        stats = {
            "queue": {
                "running": running_count,
                "pending": pending_count,
                "total": running_count + pending_count
            },
            "system": {
                "cpu_percent": cpu_percent,
                "ram_percent": ram.percent,
                "ram_free_gb": round(ram.available / (1024**3), 2),
                "ram_total_gb": round(ram.total / (1024**3), 2)
            },
            "gpu": gpu_stats,
            "is_idle": running_count == 0
        }
        
        # Build human readable summary
        summary = f"Q: {running_count} running, {pending_count} pending | CPU: {cpu_percent}% | RAM: {ram.percent}%"
        if gpu_stats and "vram_percent" in gpu_stats[0]:
            summary += f" | VRAM: {gpu_stats[0]['vram_percent']}%"
            
        return (stats, summary, stats["is_idle"])

NODE_CLASS_MAPPINGS = {
    "StatusNode": StatusNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StatusNode": "System & Queue Status"
}
