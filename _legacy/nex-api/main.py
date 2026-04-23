import os
import json
import time
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI(title="Nex Engine Intent Edition")

# ⚙️ MASTERCLASS INFRASTRUCTURE CONFIGURATION
OLLAMA_BASE = "http://nex-niflo-agent-ollama:11434"
N8N_WEBHOOK = os.getenv("N8N_WEBHOOK_URL", "http://nex-niflo-agent-n8n:5678/webhook/skill")

DEFAULT_MODEL = "qwen2.5:3b"

# 🧠 NEX INTENT ENGINE PROMPT (Unified Version)
MASTER_SYSTEM_PROMPT = """
You are Nex Intent Engine.
Your job is NOT to chat.
Your job is to DETECT USER INTENT and RETURN STRUCTURED JSON.

---

## 🧠 MODES
You ONLY respond in JSON.
There are 2 possible outputs:

---

### 1. NORMAL CHAT (NO ACTION)
{
  "intent": "none",
  "response": "..."
}

---

### 2. ACTION INTENT
{
  "intent": "create_zoom_meeting",
  "confidence": 0.0-1.0,
  "params": {
    "topic": "...",
    "datetime": "...",
    "duration": 60
  }
}

---

## 🔥 SUPPORTED INTENTS
1. create_zoom_meeting

---

## 🧠 RULES
- ALWAYS return JSON
- NEVER return text outside JSON
- NEVER explain anything
- NEVER use markdown
- NEVER include extra keys

---

## 🎯 INTENT DETECTION
Trigger "create_zoom_meeting" if user mentions:
- meeting, zoom, schedule, jadwal, buat meeting, atur meeting

---

## 🧠 PARAM EXTRACTION RULES
### topic: infer from sentence, default: "Meeting"
### datetime: MUST be ISO format: YYYY-MM-DDTHH:mm:ss
- interpret: "besok" = +1 day, "hari ini" = today, "jam 10" = 10:00
- If missing → default next day at 09:00
### duration: default = 60

---

## ⚠️ CRITICAL
If unsure → return intent: none
Accuracy > creativity | Structure > explanation
"""

def merge_prompt(user_system):
    return f"{MASTER_SYSTEM_PROMPT}\n\n--- USER PERSONA ---\n{user_system}"

def route_model(text):
    t = text.lower()
    if any(k in t for k in ["meeting", "zoom", "schedule", "jadwal", "atur"]):
        return "mistral:7b"
    if any(k in t for k in ["code", "bug", "error", "koding", "skrip", "python"]):
        return "qwen2.5-coder:7b"
    return DEFAULT_MODEL

def safe_parse(output):
    try:
        clean_output = str(output).strip()
        if "```" in clean_output:
            parts = clean_output.split("```")
            for part in parts:
                p = part.strip()
                if p.startswith("json"): p = p[4:].strip()
                if p.startswith("{") and p.endswith("}"):
                    clean_output = p
                    break
        result = json.loads(clean_output)
        if not isinstance(result, dict):
            return {"intent": "none", "response": str(result).strip()}
        return result
    except:
        return {"intent": "none", "response": str(output).strip()[:1000]}

def normalize(parsed):
    if parsed.get("intent") != "create_zoom_meeting":
        return parsed
    params = parsed.get("params", {})
    if not isinstance(params, dict): params = {}
    if "duration" not in params: params["duration"] = 60
    if "datetime" in params:
        try:
            # Ensure ISO format consistency
            dt_str = str(params["datetime"]).replace("Z", "+00:00")
            if "T" not in dt_str: # Hande simple date-only
                 dt_str = f"{dt_str}T09:00:00"
            params["datetime"] = dt_str
        except:
             params["datetime"] = (datetime.now() + timedelta(hours=1)).isoformat()
    if not params.get("topic"): params["topic"] = "Nex Intent Meeting"
    parsed["params"] = params
    return parsed

def sanitize_messages(messages):
    clean_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
        clean_messages.append({"role": str(role), "content": str(content)})
    return clean_messages

def format_sse_chunk(content_delta, role=None, finish_reason=None, model="nex-agent"):
    chunk = {
        "id": f"chatcmpl-nex-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "system_fingerprint": "fp_nex_verified_v1",
        "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": finish_reason}]
    }
    if role: chunk["choices"][0]["delta"]["role"] = role
    if content_delta: chunk["choices"][0]["delta"]["content"] = str(content_delta)
    return f"data: {json.dumps(chunk)}\n\n"

async def event_generator(final_text, model):
    yield format_sse_chunk(None, role="assistant", model=model)
    time.sleep(0.01)
    yield format_sse_chunk(final_text, model=model)
    time.sleep(0.01)
    yield format_sse_chunk(None, finish_reason="stop", model=model)
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        raw_messages = body.get("messages", [])
        clean_messages = sanitize_messages(raw_messages)
        user_input = clean_messages[-1]["content"] if clean_messages else ""
        ui_persona = next((m["content"] for m in clean_messages if m["role"] == "system"), "")
        
        # 1. SMART ROUTING
        model = route_model(user_input)
        final_system = merge_prompt(ui_persona)
        
        # 2. PREPARE PAYLOAD
        ollama_payload = {
            "model": model,
            "messages": [{"role": "system", "content": final_system}] + [m for m in clean_messages if m["role"] != "system"],
            "stream": False
        }

        # 3. NATIVE OLLAMA ENDPOINT
        target_url = f"{OLLAMA_BASE}/api/chat"
        res = requests.post(target_url, json=ollama_payload, timeout=300)
        
        if res.status_code != 200:
            return StreamingResponse(event_generator(f"Engine Error ({res.status_code})", model), media_type="text/event-stream")

        # 4. EXTRACT & GUARDRAIL
        result = res.json()
        raw_output = result.get("message", {}).get("content", "")

        parsed = safe_parse(raw_output)
        parsed = normalize(parsed)

        # 5. INTENT EXECUTION HUB
        if parsed.get("intent") == "create_zoom_meeting":
            print(f"[INTENT] Action Triggered: {parsed.get('intent')}", flush=True)
            try:
                # Mirroring keys for backward compatibility with existing n8n flows if needed
                # or just send the new params
                requests.post(N8N_WEBHOOK, json=parsed, timeout=15)
            except: pass
            final_text = f"✅ Intent Detected: `{parsed.get('intent')}`\n\n```json\n{json.dumps(parsed.get('params', {}), indent=2)}\n```"
        else:
            final_text = parsed.get("response", "Decision complete.")

        # 6. RETURN SSE STREAM
        return StreamingResponse(event_generator(final_text, model), media_type="text/event-stream")

    except Exception as e:
        print(f"[CRITICAL] Intent Engine Failure: {str(e)}", flush=True)
        return StreamingResponse(event_generator(f"System disturbance: {str(e)}", "nex-agent"), media_type="text/event-stream")

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "nex-agent", "object": "model"}]}

@app.get("/health")
async def health(): return {"status": "ok"}
