Ran command: `wsl ls -R /home/nabil/projects/nex-niflo-agent`
Ran command: `wsl cat /home/nabil/projects/nex-niflo-agent/_legacy/openclaw-config/openclaw.json`
Edited implementation_plan.md

Sebagai **AI Software Architect**, saya telah analisis infrastruktur Anda dan merekonstruksi struktur proyek menjadi arsitektur **Enterprise-Ready** yang modular, scalable, dan memisahkan setiap layer secara bersih (Clean Architecture).

Struktur lama Anda (yang sekarang ada di `_legacy`) memiliki pola _monolithic-gateway_ di mana logika routing, prompt, dan integrasi menumpuk di satu file `main.py`. Struktur baru ini akan mendistribusikan beban tersebut ke masing-masing spesialisnya.

---

### [PROJECT STRUCTURE]

```text
nex-niflo-agent/
├── .env                        # Konfigurasi rahasia global (API Keys, DB Host)
├── docker-compose.yml          # Global Orchestrator (Multi-container setup)
├── gateway/                    # LAYER 1: The Resilient Bridge (FastAPI)
│   ├── src/
│   │   ├── main.py             # Entry point API
│   │   ├── routes/             # Endpoints (chat, models, memory)
│   │   └── middleware/         # Security & Loggers
│   └── Dockerfile              # Context-specific build
├── core/                       # LAYER 2: OpenClaw Orchestrator
│   ├── orchestrator.py         # Logika koordinasi Planning & Execution
│   ├── router.py               # Smart Routing (pilih model/agent)
│   └── executor.py             # Menjalankan skill yang terpilih
├── agents/                     # LAYER 3: Agent Personas (Mental Models)
│   ├── base_agent.py           # Kelas dasar agen
│   ├── intent_agent.py         # Spesialis deteksi niat (Logic lama main.py)
│   └── researcher_agent.py     # Contoh agen spesialis pencarian
├── skills/                     # LAYER 4: Modular Tools (Capabilities)
│   ├── base_skill.py           # Interface untuk semua tool
│   ├── zoom_meeting.py         # Integrasi n8n Zoom
│   └── search_web.py           # Integrasi OpenClaw Browser
├── memory/                     # LAYER 5: Deep Intelligence
│   ├── short_term.py           # Redis client (Conversation context)
│   └── long_term.py            # Qdrant client (RAG / Vector DB)
├── integrations/               # LAYER 6: External Connectors
│   ├── ollama.py               # Native Suture ke Ollama API
│   ├── n8n.py                  # Webhook trigger client
│   └── openclaw.py             # Bridge ke OpenClaw service
├── configs/                    # Static Configuration Files
│   ├── librechat/              # librechat.yaml & presets
│   └── openclaw/               # openclaw.json
└── workspace/                  # Persistent data & logs
```

---

### [ARCHITECTURE FLOW]

1.  **Request**: **LibreChat** mengirim pesan user ke **Gateway** (FastAPI).
2.  **Context Recovery**: **Gateway** memanggil **Memory Layer** (Redis) untuk mengambil histori chat.
3.  **Intent Detection**: **Core Orchestrator** mengirim prompt ke **Ollama via Integrations** menggunakan `intent_agent` untuk mendeteksi apa mau user.
4.  **Action Trigger**: Jika terdeteksi niat "Meeting", **Orchestrator** memanggil `zoom_meeting` di **Skills Layer**.
5.  **External Automation**: **Skill** mengirim payload JSON ke **n8n** webhook.
6.  **Response Synthesis**: Hasil dari n8n digabung dengan respon AI oleh **Orchestrator**.
7.  **Streaming**: **Gateway** mengirim balik respon via Server-Sent Events (SSE) ke **LibreChat**.

---

### [FOLDER EXPLANATION]

- **`gateway/`**: Jembatan utama. Hanya fokus pada protokol HTTP, streaming, dan validasi data. Tidak boleh tahu logika "cara membuat meeting".
- **`core/`**: Otak sistem. Mengatur urutan kejadian (siapa bicara duluan, tool mana yang dipakai).
- **`agents/`**: Berisi _System Prompt_ dan parameter spesifik untuk masing-masing model (Misal: Qwen untuk Coding, Phi untuk Chat cepat).
- **`skills/`**: Tempat tool modular. Jika Anda ingin menambah tool baru (misal: kirim Email), Anda hanya perlu menambah 1 file di sini tanpa menyentuh core logic.
- **`memory/`**: Memisahkan antara ingatan jangka pendek (Redis) untuk chat saat ini, dan ingatan jangka panjang (Qdrant) untuk dokumen/PDF.

---

### [KEY FILES EXAMPLE]

#### 1. `gateway/routes/chat.py` (Resilient Entry)

```python
# Menerima request dari LibreChat
@router.post("/v1/chat/completions")
async def chat(request: ChatRequest):
    context = memory.get_context(request.user_id)
    return orchestrator.process(request, context)
```

#### 2. `skills/zoom_meeting.py` (Modular Tool)

```python
class ZoomMeetingSkill(BaseSkill):
    def execute(self, params):
        # Trigger n8n yang sudah ada
        return integrations.n8n.trigger("zoom_webhook", params)
```

---

### [ANALYSIS: OLD vs NEW]

| Aspek               | Struktur Lama (`_legacy`)                    | Struktur Baru (Ideal)                                   |
| :------------------ | :------------------------------------------- | :------------------------------------------------------ |
| **Scalability**     | Sulit. `main.py` akan jadi ribuan baris.     | Mudah. Tinggal tambah file di `/agents` atau `/skills`. |
| **Pemisahan Peran** | Monolitis (Gateway + Core jadi satu).        | Terpisah kaku (Clean Architecture).                     |
| **Debugging**       | Sulit melacak error di antara ratusan baris. | Sangat mudah melacak error per modul.                   |
| **Deployment**      | Volume mapping sederhana.                    | Build-oriented (Dockerfile per service).                |

**Insight Perbaikan:**

- **Salah Taruh**: File `openclaw.json` di root sebaiknya masuk ke folder `configs/openclaw/` agar root tetap bersih.
- **Integrasi n8n**: Di struktur lama, URL n8n dipanggil langsung di `main.py`. Di struktur baru, ini diisolasi di `integrations/n8n.py`.

Saya telah menyiapkan **Implementation Plan** mendetail di [implementation_plan.md](file:///C:/Users/Nabil/.gemini/antigravity/brain/3a686eff-381a-4a43-ae38-9a9a5fa47b9e/implementation_plan.md). Mohon tinjau rencana tersebut, terutama bagian **Open Questions** mengenai autentikasi n8n dan implementasi RAG dasar.

**Apakah Anda setuju saya mulai mengeksekusi struktur folder baru ini?**

# Implementation Plan: AI Software Architect - Project Reconstruction

Reconstructing the **Nex Niflo Agent** project from a fragmented structure into a unified, scalable, and professional AI Agent architecture based on the provided stack (LibreChat, FastAPI, OpenClaw, Ollama, n8n, Redis, Qdrant).

## User Review Required

> [!IMPORTANT]
> The current `_legacy/nex-api/main.py` is a monolithic "Intent Engine". The new plan will break this into separate modules (Gateway, Skills, Integrations). Are you comfortable with this modular approach, or do you prefer keeping the core logic in fewer files for now?

> [!WARNING]
> Moving files to the new structure will require updating all paths in the `docker-compose.yml`. I will ensure that the current "Native Suture" logic (connecting directly to Ollama when needed) is preserved in the new `integrations/ollama.py` module.

## Proposed Changes

### 1. Project Root & Infrastructure

Initialize the global configuration and environment.

#### [NEW] [.env](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/.env)

Global variables for all services (OLLAMA_URL, OPENCLAW_SECRET, REDIS_HOST, etc.).

#### [MODIFY] [docker-compose.yml](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/docker-compose.yml)

Update to reflect the new modular structure (e.g., `build: ./gateway`).

---

### 2. Gateway Layer (FastAPI)

The public interface that LibreChat talks to.

#### [NEW] [gateway/main.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/gateway/main.py)

Entry point using FastAPI, loading routes from the `routes` directory.

#### [NEW] [gateway/routes/chat.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/gateway/routes/chat.py)

Handles OpenAI-compatible `/v1/chat/completions`, delegating logic to the Core layer.

---

### 3. Core & Agent Layer (OpenClaw / Orchestator)

The "Brain" logic.

#### [NEW] [core/orchestrator.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/core/orchestrator.py)

Coordinates between Planning and Execution.

#### [NEW] [agents/intent_agent.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/agents/intent_agent.py)

Re-implementation of the "Nex Intent" legacy logic as a dedicated class.

---

### 4. Skills Layer (Modular Tools)

Modularized tools that can be triggered by agents.

#### [NEW] [skills/zoom_meeting.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/skills/zoom_meeting.py)

Logic for triggering n8n Zoom workflows.

---

### 5. Integrations & Memory

Clean connectors to external services and databases.

#### [NEW] [integrations/ollama.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/integrations/ollama.py)

Wrapper for Ollama API (Native Suture logic).

#### [NEW] [memory/redis_store.py](file:///Ubuntu/home/nabil/projects/nex-niflo-agent/memory/redis_store.py)

Handles session memory via Redis.

---

## Architecture Flow (Unified)

1. **LibreChat (UI)**: Sends `/v1/chat/completions` request to the Gateway.
2. **Gateway (FastAPI)**: Validates request and passes it to the `Core Orchestrator`.
3. **Core (Orchestrator)**:
   - Checks **Memory** (Redis) for context.
   - Consults **Intent Agent** (Ollama) to determine if an action is needed.
4. **Action Detected (e.g., Zoom)**:
   - Orchestrator calls the corresponding **Skill** (e.g., `zoom_meeting.py`).
   - Skill triggers **n8n Webhook**.
5. **Response Generation**:
   - Orchestrator combines tool output (or intent result) and sends it back to Gateway.
6. **Gateway (FastAPI)**: Streams SSE Response back to **LibreChat**.

## Open Questions

- **N8N Auth**: Do you want to use Basic Auth for the n8n webhooks, or keep them public (internal network)?
- **Qdrant RAG**: Should I implement a basic RAG skill now, or just leave the directory structure ready for it?

## Verification Plan

### Automated Tests

- `pytest` for the `gateway` endpoints.
- `wsl curl` tests for `/v1/chat/completions` to ensure streaming works.

### Manual Verification

- Deploy via `docker-compose up -d`.
- Verify LibreChat UI connects to the new Gateway.
- Trigger a Zoom intent and check if n8n receives the payload.
