# skills/automation/n8n_workflow.py
import httpx
import logging

logger = logging.getLogger("nex-skills")

async def n8n_workflow(input_data: dict):
    """
    Triggers a generic n8n automation workflow via webhook.
    Params: webhook (url), any other keys are passed as payload.
    """
    webhook = input_data.get("webhook")
    
    if not webhook:
        return {"status": "error", "message": "No webhook URL provided for n8n workflow"}

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(webhook, json=input_data, timeout=15.0)
            
            if res.status_code >= 400:
                return {
                    "status": "error", 
                    "message": f"n8n returned status {res.status_code}: {res.text[:100]}"
                }

            return {
                "status": "success", 
                "data": res.json() if res.headers.get("content-type") == "application/json" else res.text,
                "message": "n8n workflow triggered successfully"
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to trigger n8n workflow: {str(e)}"}
