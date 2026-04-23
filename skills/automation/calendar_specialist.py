# skills/automation/calendar_specialist.py
import httpx
import os
import logging

logger = logging.getLogger("nex-skills")

async def calendar_specialist(input_data: dict):
    """
    Manage Google Calendar events (List/Create) via n8n automation.
    Params: action (string: 'list' or 'create'), topic (string, for create), start_time (iso string, for create)
    """
    action = input_data.get("action", "list")
    topic = input_data.get("topic")
    start_time = input_data.get("start_time")
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    webhook_path = os.getenv("N8N_CALENDAR_WEBHOOK_PATH", "google-calendar")
    webhook_url = f"{n8n_url}/webhook/{webhook_path}"

    logger.info(f"[SKILLS] Calendar Action: {action}")
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "skill": "google_calendar",
                "action": action,
                "params": {
                    "topic": topic,
                    "start_time": start_time
                }
            }
            res = await client.post(webhook_url, json=payload, timeout=25.0)
            
            if res.status_code != 200:
                return {"status": "error", "message": f"n8n calendar error ({res.status_code}): {res.text[:100]}"}
            
            data = res.json()
            if action == "create":
                event_link = data.get("htmlLink") or data.get("link", "#")
                return {
                    "status": "success",
                    "data": data,
                    "message": f"CALENDAR_SUCCESS | Action: Create | Topic: {topic} | Time: {start_time} | Link: {event_link}"
                }
            else:
                events = data.get("events", [])
                summary = f"Anda memiliki {len(events)} agenda terdekat."
                return {
                    "status": "success",
                    "data": data,
                    "message": f"CALENDAR_SUCCESS | Action: List | Summary: {summary}"
                }
                
    except Exception as e:
        logger.error(f"[SKILLS] Calendar failed: {e}")
        return {"status": "error", "message": f"Calendar service failure: {str(e)}"}
