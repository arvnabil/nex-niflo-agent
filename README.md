# 🪐 Nex Niflo Agentic Platform (v2.2)

> **Sistem Operasi Agen AI untuk Kecerdasan Korporasi.**

Nex Niflo bukan sekadar framework AI; ini adalah **Runtime Agent Platform** yang dirancang untuk mengubah LLM menjadi perwakilan otonom yang mampu melakukan penalaran multi-langkah, orkestrasi alat (_tools_), dan manajemen memori jangka panjang.

---

## 🧠 I. Visi Proyek

Nex Niflo bergerak melampaui "AI percakapan" menuju "AI proaktif". Platform ini beroperasi sebagai lapisan antara pengguna (UI) dan komputasi dasar (Local AI/API). Dengan menerapkan **Arsitektur Split-Brain**, sistem ini menjamin stabilitas perencanaan dan eksekusi yang deterministik.

### Filosofi Utama:

- **Framework → Platform**: Dibangun untuk kasus bisnis dan skalabilitas SaaS.
- **Logika Split-Brain**: Pemisahan antara Berpikir (_Planner_) dan Bertindak (_Executor_).
- **Desain Tool-First**: Ekosistem skill modular yang membuat agen mampu berinteraksi dengan API mana pun.

---

## 🏗️ II. Arsitektur Sistem (The 6-Layer Engine)

Platform ini diatur ke dalam enam lapisan arsitektur yang bersih:

1.  **Gateway (FastAPI)**: Jembatan tangguh. Mengolah HTTP/SSE, streaming kompatibel OpenAI, dan keamanan.
2.  **Core (Orchestrator)**: "Otak" sistem. Mengelola loop ReAct (_Thought-Action-Observation_) dan pelacakan status.
3.  **Agents (Personas)**: Model mental dan _system prompt_ yang mendefinisikan identitas agen (Researcher, Specialist, dll).
4.  **Skills (Modular Tools)**: Kapabilitas modular (Produktivitas, Otomasi, Pengetahuan) yang dapat dipicu oleh agen.
5.  **Memory (Intelligence)**:
    - **Short-term**: Redis untuk alur percakapan real-time.
    - **Long-term**: Qdrant (Vector DB) untuk RAG dan memori episodik.
6.  **Integrations**: Konektor untuk mesin eksternal (Ollama, n8n, GitHub, Tavily).

---

## 🛠️ III. Ekosistem Skill

Agen memiliki akses ke registri hierarkis alat:

| Kategori         | Kapabilitas          | Alat (Tools)                           |
| :--------------- | :------------------- | :------------------------------------- |
| **Productivity** | Konten & Tugas       | Summarize, Task Reminder               |
| **Knowledge**    | Pencarian & RAG      | RAG Internal, Tavily Web Search        |
| **Automation**   | Alur Kerja Eksternal | n8n, Zoom, GitHub, ACTiV API           |
| **Agent Tools**  | Tindakan Inti        | Browser Agent, ElevenLabs TTS, Niflows |

---

## ⚡ IV. Fitur & Logika Lanjutan

- **Autonomous ReAct Loop**: Siklus koreksi diri yang mengamati hasil tool dan menyesuaikan rencana secara otomatis.
- **Anti-Repeat Protection**: Mencegah agen terjebak dalam loop pemanggilan alat yang berulang tanpa henti.
- **Max-Step Safety**: Batasan keras pada langkah penalaran untuk mengontrol latensi dan biaya.
- **Metrics & Tracing**: Pencatatan langkah-demi-langkah dari Thought, Action, dan Observation.

---

## 🚀 V. Panduan Memulai

### Prasyarat:

- Docker & Docker Compose
- NVIDIA GPU (Disarankan untuk akselerasi Ollama)
- API Keys untuk layanan eksternal (Tavily, ElevenLabs) di file `.env`

### Instalasi:

```bash
# 1. Clone repositori
git clone <repo-url>
cd nex-niflo-agent

# 2. Konfigurasi Environment
cp .env.example .env
# Edit .env dan masukkan API Keys Anda

# 3. Jalankan infrastruktur
docker-compose up -d --build
```

### Akses Layanan:

- **Chat UI**: [http://localhost:3210](http://localhost:3210) (LibreChat)
- **API Gateway**: [http://localhost:8000](http://localhost:8000)
- **n8n Dashboard**: [http://localhost:5678](http://localhost:5678)
- **Vector DB Visual**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 📈 VI. Evolusi Berikutnya (Roadmap)

Strategi kami adalah mengembangkan Nex Niflo menjadi **Self-Improving Multi-Agent System**:

1.  **Multi-Agent Communication**: Berubah dari agen tunggal menjadi klaster agen (Agent Researcher, Agent Reviewer).
2.  **Episodic Memory**: Belajar dari keberhasilan/kegagalan penggunaan tool di masa lalu.
3.  **Policy Engine**: Penambahan lapisan pengontrol untuk validasi biaya dan keamanan yang ketat.
4.  **Self-Summarizing Loop**: Kompresi memori kerja untuk menangani rantai penalaran yang sangat panjang.
5.  **Observability Dashboard**: Tracing visual real-time dari "proses berpikir" agen.

---

## 👥 VII. Kontribusi & Dukungan

Platform ini dibangun untuk skenario perusahaan berkinerja tinggi. Untuk kolaborasi atau integrasi kustom, silakan merujuk pada dokumentasi internal di folder `_legacy/docs/`.

---

---

## 🛠️ VIII. Panduan Teknis (Developer Guide)

### 1. Dokumentasi API

- **URL**: `POST /v1/chat/completions` (OpenAI Compatible)
- **Authentication**: Menggunakan `${NEX_API_KEY}` pada header untuk otorisasi.

### 2. Menambah Skill Baru

Untuk memperluas kapabilitas agen, ikuti langkah berikut:

1.  **Buat File Baru**: Tambahkan file python di dalam folder `skills/` (misal: `skills/automation/new_tool.py`).
2.  **Registrasi**: Daftarkan fungsi tersebut ke dalam `skills/registry.py` agar masuk ke dalam sistem.
3.  **Deskripsi**: Pastikan memberikan deskripsi yang jelas pada registrasi agar Planner agen bisa memahami kapan dan bagaimana menggunakan tool tersebut.

---

**Powered by Nex Sovereign Team.**
