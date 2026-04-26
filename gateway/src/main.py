import os
import time
import json
import logging
import requests
import asyncio
import uuid
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional

# Core Imports
from core.supervisor.sovereign import sovereign
from identity.linker import identity_linker
from memory.short_term import memory_store
from integrations.ollama import ollama
from observability.logger import observability
from skills.registry import registry
from agents.registry import agent_registry

# 🪵 LOGGING SETUP
logger = logging.getLogger("nex-gateway")

# 🚀 APP INITIALIZATION
app = FastAPI(title="Nex Enterprise AI Platform")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 🔐 SECURITY SETUP
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
NEX_API_KEY = os.getenv("NEX_API_KEY", "nex-sovereign-key-2026")

async def verify_api_key(request: Request, api_key_query: str = Depends(api_key_header)):
    if api_key_query == NEX_API_KEY: return api_key_query
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.replace("Bearer ", "") == NEX_API_KEY: return NEX_API_KEY
    raise HTTPException(status_code=403, detail="Invalid API Key")

# 📦 MODELS
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False

# 🧩 SSE HELPER (OpenAI compatible)
async def openai_streamer(user_id, user_input, channel="web"):
    try:
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'role': 'assistant'}}]})}\n\n"
        internal_id = identity_linker.get_internal_id(channel, user_id)
        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "user", "content": user_input, "channel": channel})
        memory_store.save(internal_id, history[-10:], segment="global")
        
        full_response = ""
        async for speaker, chunk in sovereign.process_request(internal_id, user_input, channel=channel):
            # Clean split markers for Web users
            clean_chunk = chunk.replace("[SPLIT]", "\n\n---\n\n").replace("\\n", "\n")
            full_response += clean_chunk
            model_label = f"nex-{speaker.replace('_', '-')}"
            yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'content': clean_chunk}}], 'model': model_label})}\n\n"
            await asyncio.sleep(0.05)

        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "assistant", "content": full_response})
        memory_store.save(internal_id, history[-10:], segment="global")
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"[GATEWAY] Stream Error: {e}")
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'content': f'Error: {str(e)}'}}]})}\n\n"
        yield "data: [DONE]\n\n"

# 🛣️ ROUTES
@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
@limiter.limit("20/minute")
async def chat_completions(request: Request, body: ChatRequest):
    user_input = body.messages[-1].content if body.messages else ""
    user_id = f"web_{str(uuid.uuid4())[:8]}" 
    if body.stream:
        return StreamingResponse(openai_streamer(user_id, user_input, "web"), media_type="text/event-stream")
    
    internal_id = identity_linker.get_internal_id("web", user_id)
    chunks = []
    last_speaker = "sovereign"
    async for speaker, chunk in sovereign.process_request(internal_id, user_input, channel="web"):
        chunks.append(chunk.replace("[SPLIT]", "\n---\n"))
        last_speaker = speaker
    
    response = "\n\n".join(chunks)
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "choices": [{"message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "model": f"nex-{last_speaker.replace('_', '-')}"
    }

@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    try:
        msg = update.get("message", {})
        chat_id = str(msg.get("chat", { }).get("id"))
        text = msg.get("text", "").strip()
        if not text or not chat_id: return {"ok": True}

        internal_id = identity_linker.get_internal_id("telegram", chat_id)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        if text.startswith("/"):
            # Command handling (simplified)
            command = text.split(" ")[0].lower()
            response_text = ""
            if command == "/skills": response_text = "🎯 *Skills Nex:*\n" + registry.get_skill_descriptions()
            elif command == "/help": response_text = "🤖 *Nex Help*\nKetik apapun untuk berinteraksi."
            
            if response_text and bot_token:
                requests.post(url, json={"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown"})
                return {"ok": True}
        
        # 🛡️ BUBBLE SPLITTER V3.4
        current_speaker = None
        speaker_buffer = ""
        full_response = ""
        
        if bot_token:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

        async for speaker, chunk in sovereign.process_request(internal_id, text, channel="telegram"):
            full_response += chunk
            
            # 🔥 Handle explicit [SPLIT] markers for new bubbles
            if "[SPLIT]" in chunk:
                parts = chunk.split("[SPLIT]")
                # 1. Add first part to buffer and FLUSH
                speaker_buffer += parts[0]
                if speaker_buffer.strip() and bot_token:
                    requests.post(url, json={"chat_id": chat_id, "text": speaker_buffer.strip(), "parse_mode": "Markdown"})
                
                # 2. Start new buffer with the rest
                speaker_buffer = parts[1]
                continue

            if current_speaker is None:
                current_speaker = speaker
            
            if speaker != current_speaker:
                if speaker_buffer.strip() and bot_token:
                    requests.post(url, json={"chat_id": chat_id, "text": speaker_buffer.strip(), "parse_mode": "Markdown"})
                speaker_buffer = chunk
                current_speaker = speaker
            else:
                speaker_buffer += chunk

        # Final flush
        if speaker_buffer.strip() and bot_token:
            requests.post(url, json={"chat_id": chat_id, "text": speaker_buffer.strip(), "parse_mode": "Markdown"})
        
        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "user", "content": text, "channel": "telegram"})
        history.append({"role": "assistant", "content": full_response.replace("[SPLIT]", "\n\n")})
        memory_store.save(internal_id, history[-10:], segment="global")

        return {"ok": True}
    except Exception as e:
        logger.error(f"[TELEGRAM] Webhook error: {e}")
        return {"ok": False}

@app.get("/health")
async def health():
    return {"status": "omnichannel_ready", "agents": 6}
