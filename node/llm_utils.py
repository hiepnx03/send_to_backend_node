import json
import requests
import time

class AIUniversalConnectorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_url": ("STRING", {"default": "http://localhost:11434/v1/chat/completions"}),
                "api_key": ("STRING", {"default": "ollama"}),
                "model": ("STRING", {"default": "llama3.1"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful AI assistant specialized in Stable Diffusion prompts."}),
                "user_prompt": ("STRING", {"multiline": True, "default": "Optimize this prompt: a girl in a forest"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 512, "min": 64, "max": 4096}),
            },
            "optional": {
                "history": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("response_text", "updated_history", "success")
    FUNCTION = "generate"
    CATEGORY = "API/AI"

    def generate(self, api_url, api_key, model, system_prompt, user_prompt, temperature, max_tokens, history=""):
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Parse history if provided (simple format: "User: xxx\nAssistant: yyy")
        # For professional use, we just append user_prompt
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            res_text = data['choices'][0]['message']['content']
            new_history = history + f"\nUser: {user_prompt}\nAssistant: {res_text}\n"
            
            return (res_text, new_history, True)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return (error_msg, history, False)

NODE_CLASS_MAPPINGS = {
    "AIUniversalConnectorNode": AIUniversalConnectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AIUniversalConnectorNode": "AI Universal Connector (LLM Brain)"
}
