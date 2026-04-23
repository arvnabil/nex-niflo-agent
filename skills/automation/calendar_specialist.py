import httpx
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("nex-skills")

async def calendar_list(input_data: dict):
    """List events from Google Calendar."""
    return await calendar_base_specialist({**input_data, "action": "list"})

async def calendar_create(input_data: dict):
    """Create a new event in Google Calendar."""
    return await calendar_base_specialist({**input_data, "action": "create"})

async def calendar_base_specialist(input_data: dict):
    """
    Internal base for calendar management via n8n.
    """
    action = input_data.get("action", "list")
    topic = input_data.get("topic", "Agenda Nex")
    # 🔥 Logic: If no description provided (like Zoom link), default to topic
    description = input_data.get("description") or topic
    start_time = input_data.get("start_time")
    end_time = input_data.get("end_time")
    
    # ⏰ TIMEZONE & DEFAULT LOGIC
    # Always operate in WIB (+07:00)
    now = datetime.now() # Fallback to local system time
    
    try:
        if action == "list":
            # If no start_time, default to start of today (WIB)
            if not start_time:
                start_time = now.strftime("%Y-%m-%dT00:00:00+07:00")
            # If no end_time, default to end of today (WIB)
            if not end_time:
                end_time = now.strftime("%Y-%m-%dT23:59:59+07:00")
        
        elif action == "create":
            if not start_time:
                logger.error("[SKILLS] FATAL ERROR: No start_time provided for creation!")
                return {"status": "error", "message": "FAILED: Anda lupa menyertakan 'start_time' di perintah kalender. Ambil waktu dari hasil Zoom tadi dan coba lagi secara akurat!"}
            
            # Ensure start_time has TZ offset if missing
            if "T" in start_time and "+" not in start_time and "Z" not in start_time:
                start_time = f"{start_time}+07:00"

            if not end_time:
                try:
                    st_dt = datetime.fromisoformat(start_time.replace("+07:00", "+07:00"))
                    # If it's UTC (Z), convert or handle
                    effective_dt = st_dt
                    end_time = (effective_dt + timedelta(hours=1)).isoformat()
                    if "+" not in end_time and "Z" not in end_time:
                        end_time = f"{end_time}+07:00"
                except Exception as e:
                    logger.error(f"Error calculating end_time: {e}")
                    end_time = start_time

    except Exception as te:
        logger.warning(f"[SKILLS] Calendar time parsing warning: {te}")
        # Fallback to whatever we have if logic fails
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    webhook_path = os.getenv("N8N_CALENDAR_WEBHOOK_PATH", "google-calendar")
    webhook_url = f"{n8n_url}/webhook/{webhook_path}"

    logger.warning(f"[CALENDAR-SKILL] ACTION SENDING: {action} | Topic: {topic} | Start: {start_time}")
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "skill": "google_calendar",
                "action": action,
                "params": {
                    "topic": topic,
                    "description": description,
                    "start_time": start_time,
                    "end_time": end_time
                }
            }
            res = await client.post(webhook_url, json=payload, timeout=25.0)
            
            if res.status_code != 200:
                return {"status": "error", "message": f"n8n calendar error ({res.status_code}): {res.text[:100]}"}
            
            data = res.json()
            
            # 🎨 PRE-FORMATTED MESSAGE HANDLING
            # If the user used a Function node in n8n to format the response
            # we prioritize that 'message' key.
            n8n_message = ""
            if isinstance(data, list) and len(data) > 0:
                n8n_message = data[0].get("json", {}).get("message") or data[0].get("message")
            elif isinstance(data, dict):
                n8n_message = data.get("message")
                
            if n8n_message:
                return {"status": "success", "message": n8n_message}

            if action == "create":
                # Handle direct object or list from n8n for manual creation
                obj = data[0] if isinstance(data, list) else data
                if isinstance(obj, dict) and "json" in obj: obj = obj["json"]
                
                event_link = obj.get("htmlLink") or obj.get("link", "#")
                return {
                    "status": "success",
                    "data": data,
                    "message": f"CALENDAR_SUCCESS | Action: Create | Topic: {topic} | Time: {start_time} | Link: {event_link}"
                }
            else:
                # 🛡️ FLEXIBLE EVENT EXTRACTION (LIST)
                events = []
                if isinstance(data, list):
                    events = data
                elif isinstance(data, dict):
                    events = data.get("events") or data.get("items") or [data]
                
                # Check for n8n wrapper
                if isinstance(events, list) and len(events) > 0 and isinstance(events[0], dict) and "json" in events[0]:
                    events = [e["json"] for e in events]

                if not events or (isinstance(events, list) and len(events) == 0) or (isinstance(events[0], dict) and not events[0].get('kind')):
                    return {"status": "success", "message": "Anda tidak memiliki agenda terjadwal untuk periode ini."}
                
                summary = f"Anda memiliki {len(events)} agenda terdekat."
                event_details = "\n".join([f"• {e.get('summary')} ({e.get('start', {}).get('dateTime', 'Waktu tidak tersedia')})" for e in events[:5]])
                return {
                    "status": "success",
                    "data": data,
                    "message": f"CALENDAR_SUCCESS | Action: List | {summary}\n{event_details}"
                }
                
    except Exception as e:
        logger.error(f"[SKILLS] Calendar failed: {e}")
        return {"status": "error", "message": f"Calendar service failure: {str(e)}"}
