import requests
import os
import json

class OpenAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        
    def chat(self, model, messages, stream=False, **kwargs):
        """
        Calls OpenAI Chat Completions API.
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env")
            
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        # We wrap the response in an object that looks like requests.Response 
        # to maintain compatibility with the existing code's usage of res.json()
        return requests.post(url, headers=headers, json=payload, stream=stream)

    def embed(self, model, prompt):
        """
        Calls OpenAI Embeddings API (default: text-embedding-3-small).
        """
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": prompt,
            "model": model or "text-embedding-3-small"
        }
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", [{}])[0].get("embedding")
        return None

# Singleton instance
openai_provider = OpenAIClient()
