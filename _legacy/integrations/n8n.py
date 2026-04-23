import requests
import os
import json
import logging

class N8NClient:
    def __init__(self, base_url=None, user=None, password=None):
        self.base_url = base_url or os.getenv("N8N_URL", "http://nex-niflo-agent-n8n:5678")
        self.user = user or os.getenv("N8N_USER", "admin")
        self.password = password or os.getenv("N8N_PASSWORD", "admin")
        
    def trigger_webhook(self, path, payload):
        url = f"{self.base_url}/webhook/{path}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Diagnostic logging for audit
        logging.info(f"[N8N-DIAG] Sending to: {url}")
        logging.info(f"[N8N-DIAG] Payload: {json.dumps(payload)}")
        
        try:
            res = requests.post(
                url, 
                json=payload, 
                auth=(self.user, self.password),
                headers=headers,
                timeout=20
            )
            logging.info(f"[N8N-DIAG] Status: {res.status_code}")
            return res.status_code, res.text
        except Exception as e:
            logging.error(f"[N8N-DIAG] Request Failed: {str(e)}")
            return 500, str(e)

# Singleton instance
n8n = N8NClient()
