import os
import json
import time
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI(title="Nex-Niflo Agent API")

OLLAMA_BASE_URL = "http://nex-niflo-agent-ollama:11434"
DEFAULT_OLLAMA_MODEL = "mistral:7b"

def fetch_ollama_models():
    """Mengambil daftar model asli dari API Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name") for m in models]
    except Exception as e:
        print(f"[ERROR] Failed to fetch Ollama models: {str(e)}", flush=True)
    return [DEFAULT_OLLAMA_MODEL]

def sanitize_messages(messages):
    """Standarisasi format pesan agar kompatibel dengan seluruh model Ollama"""
    clean_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if isinstance(content, list):
            flattened_text = ""
            for part in content:
                if isinstance(part, dict):
                    flattened_text += part.get("text", "")
                elif isinstance(part, str):
                    flattened_text += part
            content = flattened_text
        
        clean_messages.append({
            "role": str(role),
            "content": str(content)
        })
    return clean_messages

def create_completion_response(content, model="gpt-5"):
    timestamp = int(time.time())
    return {
        "id": f"chatcmpl-{timestamp}",
        "object": "chat.completion",
        "created": timestamp,
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": len(content.split()), "total_tokens": 10 + len(content.split())}
    }

async def generate_ollama_stream(payload, model="gpt-5"):
    timestamp = int(time.time())
    chat_id = f"chatcmpl-{timestamp}"
    
    # Send initial role chunk
    start_chunk = {
        "id": chat_id, "object": "chat.completion.chunk", "created": timestamp, "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}]
    }
    yield f"data: {json.dumps(start_chunk)}\n\n"

    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=180)
        response.raise_for_status()
        
        for line in response.iter_lines(chunk_size=1):
            if line:
                chunk_data = json.loads(line.decode())
                content = chunk_data.get("message", {}).get("content", "")
                done = chunk_data.get("done", False)

                openai_chunk = {
                    "id": chat_id, "object": "chat.completion.chunk", "created": timestamp, "model": model,
                    "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": "stop" if done else None}]
                }
                yield f"data: {json.dumps(openai_chunk)}\n\n"
                if done: break
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        print(f"[ERROR] Stream interrupted: {str(e)}", flush=True)
        error_msg = "\n\n[Error: " + str(e) + "]"
        err_obj = {"choices": [{"delta": {"content": error_msg}}]}
        yield f"data: {json.dumps(err_obj)}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        requested_model = body.get("model", "gpt-5")
        stream = body.get("stream", False)
        
        actual_model = DEFAULT_OLLAMA_MODEL if requested_model == "gpt-5" else requested_model
        
        clean_messages = sanitize_messages(body.get("messages", []))
        
        print(f"[LOG] Routing Request: {requested_model} -> {actual_model} (stream={stream})", flush=True)

        ollama_payload = {
            "model": actual_model,
            "messages": clean_messages,
            "stream": stream
        }

        if stream:
            headers = {
                "Content-Type": "text/event-stream; charset=utf-8",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
            return StreamingResponse(generate_ollama_stream(ollama_payload, model=requested_model), headers=headers)
        else:
            response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=ollama_payload, timeout=180)
            if response.status_code == 200:
                ai_content = response.json().get("message", {}).get("content", "")
                return create_completion_response(ai_content, model=requested_model)
        
        return JSONResponse(status_code=500, content={"error": "Ollama Error"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/v1/models")
async def list_models():
    ollama_models = fetch_ollama_models()
    openai_models = [{"id": "gpt-5", "object": "model", "created": int(time.time()), "owned_by": "nex-niflo"}]
    for model_name in ollama_models:
        openai_models.append({"id": model_name, "object": "model", "created": int(time.time()), "owned_by": "ollama-local"})
    return {"object": "list", "data": openai_models}

@app.get("/health")
async def health(): return {"status": "ok"}
