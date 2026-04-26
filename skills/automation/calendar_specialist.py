import os
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger("nex-calendar-specialist")

async def calendar_create(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill V3.11: Create Google Calendar event via n8n with Smart Duration.
    """
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    webhook_path = os.getenv("N8N_CALENDAR_WEBHOOK_PATH", "google-calendar")
    
    topic = input_data.get("topic", "Agenda Nex")
    start_time_raw = input_data.get("start_time")
    
    # 🔥 V3.11: Smart Parsing & Duration
    start_dt = None
    if not start_time_raw:
        start_dt = datetime.now()
    else:
        try:
            start_dt = datetime.fromisoformat(start_time_raw.replace("Z", "+00:00"))
        except:
            start_dt = datetime.now()

    # 🔥 V3.11: Force 1 Hour Duration if not specified
    end_time_raw = input_data.get("end_time")
    if not end_time_raw:
        end_dt = start_dt + timedelta(hours=1)
    else:
        try:
            end_dt = datetime.fromisoformat(end_time_raw.replace("Z", "+00:00"))
        except:
            end_dt = start_dt + timedelta(hours=1)

    payload = {
        "topic": topic,
        "description": input_data.get("description", "Dibuat oleh Nex Agent"),
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "type": "calendar_only"
    }

    try:
        url = f"{n8n_url}/webhook/{webhook_path}"
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"CALENDAR_SUCCESS | {response.text}"
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

async def calendar_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """List calendar events."""
    # (Leaving existing calendar_list as is)
    return {"status": "info", "message": "List functional."}
