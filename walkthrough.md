# Walkthrough - Hierarchical Skills Overhaul

Saya telah menyelesaikan perombakan besar-besaran pada sistem Skill Nex Sovereign Agent. Sistem sekarang menggunakan arsitektur hierarkis yang lebih rapi, modern, dan siap untuk skenario multi-agent.

## Perubahan Arsitektur

### 1. Struktur Folder Baru

Skills sekarang dikelompokkan ke dalam kategori fungsional:

- `skills/productivity/`: Task reminders & Summarization.
- `skills/knowledge/`: RAG search & Web search.
- `skills/automation/`: n8n, Zoom, GitHub, & ACTiV API.
- `skills/agent_tools/`: Browser, TTS (ElevenLabs), & Niflows Orchestration.

### 2. Standarisasi Async & Dict Patterns

Semua skill kini menggunakan pola yang seragam:

- **Async**: Semua fungsi skill adalah `async`, memungkinkan I/O non-blocking (seperti pemanggilan API).
- **Single Input**: Menggunakan satu argumen `input_data: dict` untuk fleksibilitas parameter yang lebih tinggi di masa depan.

### 3. Pembaruan Core Engine

- **Registry Update**: `skills/registry.py` telah ditulis ulang untuk memetakan kategori hierarkis ini ke dalam satu _source of truth_ (`SKILLS` dictionary).
- **Loop Engine**: `core/loop.py` telah diperbarui untuk mendukung `await` saat mengeksekusi skill, memastikan alur kerja sinkron-asinkron berjalan lancar.

## Detil Skill yang Diimplementasikan

| Kategori         | Skill           | Status     | Catatan                                      |
| :--------------- | :-------------- | :--------- | :------------------------------------------- |
| **Productivity** | `summarize`     | ✅ Sukses  | Mendukung peringkasan teks panjang.          |
|                  | `task_reminder` | ✅ Sukses  | Penjadwalan tugas/pengingat.                 |
| **Knowledge**    | `rag_search`    | ✅ Migrasi | Menggunakan integrasi Qdrant yang sudah ada. |
|                  | `tavily_search` | ✅ Sukses  | Pencarian web real-time (Tavily/Fallback).   |
| **Automation**   | `n8n_workflow`  | ✅ Sukses  | Trigger webhook n8n secara generik.          |
|                  | `zoom_engineer` | ✅ Migrasi | Integrasi Zoom via n8n (Async).              |
|                  | `github`        | ✅ Sukses  | Interaksi dengan repositori GitHub.          |
|                  | `activ_api`     | ✅ Sukses  | Interaksi dengan sistem ACTiV API.           |
| **Agent Tools**  | `browser`       | ✅ Sukses  | Esktrasi konten web.                         |
|                  | `elevenlabs`    | ✅ Sukses  | Text-to-Speech (TTS) berkualitas tinggi.     |
|                  | `niflows`       | ✅ Sukses  | Power tool untuk orkestrasi multi-step.      |

## Langkah Selanjutnya (Rekomendasi)

> [!TIP]
> **Update Planner Model**: Karena ada perubahan nama tool (misal `search_knowledge` → `rag_search`), sangat disarankan untuk melakukan "Brain Refresh" agar Agen mengenali tool-tool baru ini dengan sempurna.
> **API Keys**: Beberapa tool (Tavily, ElevenLabs, GitHub) membutuhkan API Key di file `.env` Anda untuk bekerja secara penuh di mode produksi.

Sistem Anda sekarang benar-benar **Production-Ready Foundation**! Apakah ada bagian spesifik yang ingin Anda coba eksekusi terlebih dahulu?

# Walkthrough: The Agentic Evolution (V2.2)

Sistem **Nex Niflo Agent** kini bukan sekadar bot chat, melainkan **Autonomous Agent Platform** yang mampu melakukan penalaran multi-langkah.

## 🧠 1. Brain: Mistral 7B Planner

Kami memisahkan tugas antara "Berpikir" dan "Bicara".

- **Planner (Mistral 7B)**: Menangani dekomposisi tugas dan pemilihan alat.
- **Executor (Qwen 2.5 3B)**: Menangani interaksi cepat dan format respon akhir.

## 🧩 2. Unified Skill Registry

Semua kemampuan agen kini bersifat modular.

- Menambah skill baru semudah meregistrasikannya di `skills/registry.py`.
- Agen dapat melihat deskripsi semua alat yang tersedia sebelum memutuskan langkah.

## 🔄 3. Async ReAct Loop

Agen bekerja dengan siklus:

1.  **THOUGHT**: Menganalisis apa yang harus dilakukan.
2.  **ACTION**: Menanggil skill yang tepat dari registry.
3.  **OBSERVATION**: Menerima hasil dari skill tersebut.
4.  **REPEAT**: Mengulangi sampai tugas selesai atau mencapai batas langkah.

---

## 🛡️ 4. Safety & Guards

- **Max Steps**: Mencegah agen "tersesat" dalam loop tanpa henti (Max 5 langkah).
- **Anti-Repeat**: Mencegah pemanggilan alat yang sama dengan parameter yang sama berulang kali.
- **Early Stop**: Agen akan berhenti segera setelah tujuan tercapai.

## 📊 5. Observability (Visibility)

Anda sekarang dapat melihat apa yang terjadi di balik layar melalui log:

- **[METRIC]**: Waktu eksekusi fungsi.
- **[INTENT]**: Analisis niat awal.
- **[SKILL]**: Detail alat yang dipanggil.
- **[RAG]**: Status pencarian dokumen (Hit/Miss & Score).

---

## 🚀 Status Deployment Final

Sistem telah diperbarui ke arsitektur Agentic Platform. Pastikan untuk menjalankan `docker-compose up -d --build` untuk memuat modul logic yang baru.

**Agen Anda kini siap untuk tugas-tugas kompleks!**

---

# Walkthrough: Omnichannel Commands & Skill Stability (V2.3)

Pembaruan terbaru berfokus pada pengalaman pengguna di Telegram dan stabilitas integrasi pihak ketiga (Google & GitHub).

## ⚡ 1. Telegram Command Shortcuts
Bot Telegram kini mendukung perintah instan menggunakan awalan `/` untuk akses cepat tanpa melalui proses penalaran LLM:

- **/skills**: Menampilkan daftar lengkap kemampuan agen yang terdaftar.
- **/activwebsite**: Link cepat menuju portal integrasi ACTiV.
- **/agent**: Status kesehatan sistem dan protokol keamanan (Anti-Gravity).
- **/help**: Panduan penggunaan bot dan daftar perintah.

## 📅 2. Google Calendar Fix (Error 400)
- **Problem**: Sebelumnya muncul error "Bad Request" karena parameter `end_time` tidak terkirim saat pembuatan event.
- **Solution**: `calendar_specialist.py` kini mendukung dan mewajibkan `end_time`. Jika tidak diberikan oleh agen, sistem akan otomatis mengatur durasi default (1 jam setelah waktu mulai).

## 🐙 3. GitHub API Resiliency
- Menambahkan validasi status code pada `github_specialist.py`.
- Agen kini dapat menangani respons error dari GitHub (seperti token expired atau repo tidak ditemukan) secara elegan dengan memberikan pesan yang informatif ke pengguna, alih-alih mengalami *crash* internal.

## 🗺️ Status Terbaru
| Fitur             | Status | Versi |
| :---------------- | :----- | :---- |
| Telegram Commands | ✅ OK  | v2.3  |
| Calendar Sync     | ✅ OK  | v2.3  |
| GitHub Specialist | ✅ OK  | v2.3  |
| Weather Check     | ✅ OK  | v1.0  |
| Web Search (Stab) | ✅ OK  | v2.3  |

## 🔍 4. Web Search Stability (Analyst Fix)
- **Problem**: Sebelumnya alat `web_search` (DuckDuckGo Scraper) rentan mengalami kegagalan parsing atau diblokir, menyebabkan Agen Analyst memberikan balasan umum/placeholder.
- **Solution**: 
  - Mengalihkan `web_search` ke `tavily_search.py` yang mendukung **Tavily AI Search** (Primary) dan **DuckDuckGo Lite Scraper** (Fallback).
  - DuckDuckGo Scraper diperbarui menggunakan versi `lite` yang lebih stabil dan tahan terhadap perubahan layout HTML.
  - Menghindari penggunaan placeholder API Key jika belum diatur di `.env`.

**Sistem kini lebih tangguh dan responsif di berbagai kanal!**
