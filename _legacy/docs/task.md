- [x] **Phase 1: Environment & Directory Setup**
    - [x] Create folder structure (gateway, core, agents, skills, rag, integrations, memory, configs)
    - [x] Create `.env` with initial keys
    - [x] Update `docker-compose.yml` (Internalizing ports, build contexts)

- [x] **Phase 2: Core Integrations & Memory**
    - [x] Implement `integrations/ollama.py` (with lazy-pull logic)
    - [x] Implement `integrations/n8n.py`
    - [x] Implement `memory/short_term.py` (Redis)
    - [x] Implement `memory/long_term.py` (Qdrant with required schema)

- [x] **Phase 3: RAG Implementation**
    - [x] Implement `rag/ingest/loader.py`
    - [x] Implement `rag/vectorstore/qdrant.py`
    - [x] Implement `rag/generation/rag_chain.py` (with safety guards)

- [x] **Phase 4: Agent Logic & Orchestration**
    - [x] Implement `agents/intent_agent.py` (Migration from legacy)
    - [x] Implement `core/orchestrator.py`
    - [x] Implement `skills/zoom_meeting.py`

- [x] **Phase 5: Gateway & Security**
    - [x] Implement `gateway/src/main.py` (FastAPI, Header API Key, Logging)
    - [x] Implement Rate Limiting middleware
    - [x] Create `gateway/Dockerfile`

- [x] **Phase 6: Deployment & Verification**
    - [x] Build and start containers
    - [x] Verify internal communication (n8n, qdrant, redis)
    - [x] End-to-end test with LibreChat
