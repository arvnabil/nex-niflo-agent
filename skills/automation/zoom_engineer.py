import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("nex-zoom-engineer")

async def zoom_engineer(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill V3.5: Zoom Only Call.
    Webhook: zoom-meeting
    """
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    
    # 🔥 V3.5 MANDATE: Use zoom-meeting for Zoom Only
    webhook_path = "zoom-meeting"
    
    topic = input_data.get("topic", "Nex Zoom Sync")
    start_time = input_data.get("start_time") or input_data.get("datetime_iso")
    
    if not start_time:
        from datetime import datetime
        start_time = datetime.now().isoformat()

    payload = {
        "topic": topic,
        "start_time": start_time,
        "host_email": input_data.get("host_email", "support@activ.co.id"),
        "type": "zoom_only"
    }

    try:
        full_url = f"{n8n_url}/webhook/{webhook_path}"
        logger.info(f"[ZOOM-V3.5] Triggering ZOOM-ONLY Webhook: {full_url}")
        
        response = requests.post(full_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"ZOOM_ONLY_SUCCESS | {response.text}"
            }
        else:
            return {
                "status": "error",
                "message": f"n8n rejection: {response.text}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"n8n connection failed: {str(e)}"
        }
