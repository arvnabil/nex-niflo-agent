import requests
import json
import os
import threading
import time

class OllamaClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://nex-niflo-agent-ollama:11434")
        self.pulled_models = set()
        
    def lazy_pull(self, model_name):
        """Non-blocking check and pull of model."""
        def pull_worker():
            try:
                # Check if model exists
                res = requests.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m["name"] for m in res.json().get("models", [])]
                    if any(model_name in m for m in models):
                        print(f"[OLLAMA] Model {model_name} already exists. Skipping pull.", flush=True)
                        self.pulled_models.add(model_name)
                        return
                
                print(f"[OLLAMA] Pulling model {model_name} in background...", flush=True)
                requests.post(f"{self.base_url}/api/pull", json={"name": model_name}, timeout=600)
                print(f"[OLLAMA] Model {model_name} pull complete.", flush=True)
                self.pulled_models.add(model_name)
            except Exception as e:
                print(f"[OLLAMA] Pull failed for {model_name}: {str(e)}", flush=True)

        # Run in separate thread to avoid blocking startup
        thread = threading.Thread(target=pull_worker)
        thread.daemon = True
        thread.start()

    def chat(self, model, messages, stream=False, **kwargs):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        return requests.post(url, json=payload, stream=stream)

    def embed(self, model, prompt):
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": model,
            "prompt": prompt
        }
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json().get("embedding")
        return None

# Singleton instance
ollama = OllamaClient()
