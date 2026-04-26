import os
import requests
import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger("nex-zcalendar-hybrid")

async def zcalendar_create(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Super-Skill V3.11: Hybrid Call with Smart Duration (Default 1 Hour).
    Webhook: nex-gc-zoom
    """
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    webhook_path = "nex-gc-zoom"
    
    topic = input_data.get("topic", "Niflo Meeting")
    start_time_raw = input_data.get("start_time")
    end_time_raw = input_data.get("end_time")
    
    # 🔥 V3.8/V3.11: ADVANCED TIME DETECTION (AM/PM)
    start_dt = None
    if not start_time_raw:
        task_lower = topic.lower()
        time_match = re.search(r"(?:jam|pukul)\s*(\d+)", task_lower)
        if time_match:
            hour = int(time_match.group(1))
            if any(kw in task_lower for kw in ["malam", "sore", "pm"]):
                if hour < 12: hour += 12
            now = datetime.now()
            start_dt = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            start_dt = datetime.now()
    else:
        try:
            # Handle ISO format
            start_dt = datetime.fromisoformat(start_time_raw.replace("Z", "+00:00"))
        except:
            start_dt = datetime.now()

    # 🔥 V3.11: SMART DURATION (Default 1 Hour)
    if not end_time_raw:
        end_dt = start_dt + timedelta(hours=1)
    else:
        try:
            end_dt = datetime.fromisoformat(end_time_raw.replace("Z", "+00:00"))
        except:
            end_dt = start_dt + timedelta(hours=1)

    payload = {
        "topic": topic,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "host_email": input_data.get("host_email", "support@activ.co.id"),
        "type": "hybrid"
    }

    try:
        import json
        full_url = f"{n8n_url}/webhook/{webhook_path}"
        logger.info(f"[ZCAL-V3.11] Triggering Webhook: {full_url} | Start: {payload['start_time']} -> End: {payload['end_time']}")
        
        response = requests.post(full_url, json=payload, timeout=12)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"HYBRID_SUCCESS | {response.text}"
            }
        else:
            return {
                "status": "error",
                "message": f"n8n REJECTED ({response.status_code}): {response.text}"
            }
    except Exception as e:
        logger.error(f"[ZCAL] Error: {e}")
        return {
            "status": "error",
            "message": f"CRITICAL_CONNECTION_ERROR: {str(e)}"
        }
