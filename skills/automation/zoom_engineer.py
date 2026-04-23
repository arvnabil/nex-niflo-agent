# skills/automation/zoom_engineer.py
import httpx
import os
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger("nex-skills")

async def zoom_engineer(input_data: dict):
    """
    Schedules a Zoom meeting via n8n automation.
    Params: topic (string), datetime_iso (string), duration (int, optional), host_email (string, optional)
    """
    topic = input_data.get("topic")
    datetime_iso = input_data.get("datetime_iso")
    duration = input_data.get("duration", 60)
    host_email = input_data.get("host_email", "support@activ.co.id")
    
    if not topic or not datetime_iso:
        return {"status": "error", "message": "Missing required params: topic and datetime_iso"}

    # Timezone check: Ensure it has +07:00 if no TZ specified
    if "T" in datetime_iso and "+" not in datetime_iso and "Z" not in datetime_iso:
        datetime_iso = f"{datetime_iso}+07:00"

    # Environment configuration
    n8n_url = os.getenv("N8N_URL", "http://nex-niflo-agent-n8n:5678")
    webhook_path = os.getenv("N8N_ZOOM_WEBHOOK_PATH", "zoom-meeting")
    webhook_url = f"{n8n_url}/webhook/{webhook_path}"

    try:
        # Pastikan start_time_wib adalah FULL ISO string dengan offset +07:00 agar n8n (JavaScript) tidak Invalid Date
        iso_with_tz = datetime_iso
        if "T" in iso_with_tz and "+" not in iso_with_tz and "Z" not in iso_with_tz:
            iso_with_tz = f"{iso_with_tz}+07:00"
        
        # Sediakan juga display_time untuk n8n jika ingin menampilkan jam (HH:MM) saja secara aman
        display_time = iso_with_tz.split("T")[1][:5] if "T" in iso_with_tz else iso_with_tz
        
        # Calculate end_time
        try:
            st_dt = datetime.fromisoformat(iso_with_tz.replace("Z", "+00:00"))
            end_time = (st_dt + timedelta(minutes=duration)).isoformat()
        except:
            end_time = iso_with_tz
        
        data_packet = {
            "skill": "zoom_meeting",
            "params": {
                "topic": topic,
                "start_time": datetime_iso,
                "end_time": end_time,
                "start_time_wib": iso_with_tz,
                "display_time": f"{display_time} WIB",
                "duration": duration,
                "host_email": host_email
            }
        }
        
        payload = {**data_packet, "json": data_packet}
        
        async with httpx.AsyncClient() as client:
            res = await client.post(webhook_url, json=payload, timeout=20.0)
            
            status = res.status_code
            result = res.text
            
            if status != 200:
                return {"status": "error", "message": f"n8n failed ({status}): {result[:100]}"}

            try:
                res_json = res.json()
                join_url = res_json.get("join_url") or res_json.get("join_link")
                meeting_id = res_json.get("id", "-")
                host_val = res_json.get("host", "support@activ.co.id")
                passcode = res_json.get("password") or res_json.get("passcode", "-")
                
                if join_url:
                    # Success message in a very structured format for the agent
                    return {
                        "status": "success",
                        "message": f"ZOOM_SUCCESS | Topic: {topic} | Jam: {display_time} WIB | Raw_Start: {iso_with_tz} | Raw_End: {end_time} | Link: {join_url} | ID: {meeting_id} | Host: {host_val}",
                        "data": res_json
                    }
                else:
                    return {"status": "error", "message": "n8n response missing join_url"}
            except Exception as e:
                return {"status": "error", "message": f"Invalid JSON from n8n: {str(e)}"}
                
    except Exception as e:
        logger.error(f"[ZOOM-ENGINEER] Exception: {str(e)}")
        return {"status": "error", "message": f"Zoom Engineer critical failure: {str(e)}"}
