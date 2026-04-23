# Implementation Plan: AI Software Architect - Project Reconstruction (V2 with RAG & Security)

Reconstructing the **Nex Niflo Agent** project with a focus on security, a minimal but scalable RAG system, and an internal-only automation layer.

## User Review Required

> [!IMPORTANT]
> **Internal-only n8n**: I will remove the port mapping `5678:5678` from the `docker-compose.yml` for n8n to ensure it is only accessible within the Docker network. Access for maintenance will be via the host or a temporary proxy if needed.
> 
> **FastAPI Security**: I will implement a custom API Key middleware. LibreChat will need to be configured to pass this key.

> [!TIP]
> **Ollama Embeddings**: We will use `nomic-embed-text` or similar via Ollama for a 100% local embedding process.

## Proposed Changes

### 1. Global Networking & Security
#### [MODIFY] [docker-compose.yml](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/docker-compose.yml)
- Remove public exposure for `n8n`, `qdrant`, and `redis`.
- Keep only `librechat` (UI) and `gateway` (API) exposed if necessary, or just `librechat` if it proxies everything.
#### [NEW] [.env](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/.env)
- Add `NEX_API_KEY=your-secure-key`.
- Add `N8N_BASIC_AUTH_PASS`.

---

### 2. Gateway Layer (FastAPI Security)
#### [MODIFY] [gateway/main.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/gateway/src/main.py)
- Incorporate API Key validation middleware.

---

### 3. RAG System (Minimal & Scalable)
New directory `rag/` in the root or within the backend context.

#### [NEW] [rag/ingest/loader.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/rag/ingest/loader.py)
Logic to load PDF and Text files.
#### [NEW] [rag/vectorstore/qdrant.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/rag/vectorstore/qdrant.py)
Wrapper for Qdrant client to search and save.
#### [NEW] [rag/generation/rag_chain.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/rag/generation/rag_chain.py)
The core logic for Context Injection into the LLM prompt.

---

### 4. Agent Core (OpenClaw Decision)
#### [MODIFY] [core/router.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/core/router.py)
- Add "RAG" as a possible intent/direct tool when the user asks questions about their local knowledge.

---

## Technical Data Flow

1. **User** asks a question in **LibreChat**.
2. **FastAPI Gateway** validates the API Key and passes request to **Orchestrator**.
3. **Orchestrator** (via **Intent Agent**) decides: "Does this require local knowledge?"
4. If YES:
   - **Retriever** converts query to embedding via **Ollama**.
   - **Qdrant** returns top-5 matches.
   - **RAG Chain** injects context into the prompt.
5. **Ollama** generates response with local knowledge.
6. **FastAPI** streams to User.

## Open Questions

- **Embedding Model**: Should I automatically pull `nomic-embed-text` (approx 274MB) for you?
- **n8n Access**: Since I'm removing the public port for security, how do you prefer to access the n8n UI for workflow building (e.g., SSH tunnel, temporary port exposure, or via a specific sub-path)?

## Verification Plan

### Automated Tests
- Script to ingest a sample text file and verify it exists in Qdrant.
- Mock request to Gateway without API Key (should fail).
- Mock request with API Key (should succeed).

### Manual Verification
- Ask the agent about the content of a uploaded/ingested file.
- Check n8n logs via `docker logs` to ensure internal communication is working.
