# Masterclass: Mastering Local AI Sovereignty 👑💎
**Panduan Arsitektur Nex Agent Engine: Menaklukkan Cloud-Centric Binary demi Kedaulatan Lokal.**

Oleh: **Antigravity (Google Deepmind)**

---

## Pendahuluan: Filosofi Sovereignty
Dalam dunia AI, "Kedaulatan" berarti Anda memiliki kontrol penuh atas pikiran mesin Anda. Masalah yang kita hadapi pada pengembangan **Nex Agent Engine** adalah sebuah sistem (OpenClaw) yang dirancang untuk sangat bergantung pada OpenAI (Cloud). 

Misi kita: **Memaksa sistem ini berpikir bahwa ia sedang bicara dengan OpenAI, padahal ia sedang bicara dengan Ollama lokal Anda.**

---

## Bab 1: Trinitas Kegagalan (The 400, 404, 500 Crisis)

Sebelum kita mulai melakukan "Sihir", kita menabrak tiga tembok besar:
1.  **Error 400 (Bad Request)**: Sistem menolak data JSON yang masuk.
2.  **Error 404 (Not Found)**: Gerbang komunikasi tertutup atau salah alamat.
3.  **Error 500 (Internal Server Error)**: Sistem mengalami "Krisis Identitas" karena kunci (Auth) tidak cocok.

> [!IMPORTANT]
> **Pelajaran Utama**: Jangan pernah meremehkan integritas biner. Sedikit saja kita mengubah label identitas di dalam file yang sudah terkompilasi, protokol komunikasi (seperti JSON parse) bisa hancur.

---

## Bab 2: DNA Restoration (Kenapa DNA 'OpenAI' Penting?)

### Masalah:
Kita mencoba mengubah semua kata `openai` menjadi `ollama` di dalam file biner (`dist/*.js`). 
**Hasilnya?** Error 400. Kenapa? Karena di dalam kode yang sudah terkompilasi, label `openai` bukan sekadar nama, tapi kunci untuk memanggil fungsi-fungsi pemroses JSON tertentu. Saat namanya diganti, fungsi itu hilang, dan sistem tidak tahu cara membaca pesan lagi.

### Sihir (Resolve):
Saya melakukan **DNA Restoration**. Saya mengembalikan identitas biner kembali menjadi `openai`. 
**Logikanya**: Biarkan sistem merasa ia adalah OpenAI di "Luar", tapi kita akan sabotase arah jalannya di "Dalam".

---

## Bab 3: Master Key Injection (Rahasia Gembok 500)

### Masalah:
Sistem terus memuntahkan Error 500 karena ia mencari kunci rumah (API Key) dan tidak menemukannya. Struktur file `auth-profiles.json` yang kita buat sebelumnya ternyata tidak sesuai dengan apa yang diharapkan oleh mata biner OpenClaw.

### Sihir (Resolve):
Saya membongkar file biner `profiles-CVErLX2C.js` dan menemukan skema yang benar. 
**Kuncinya adalah struktur `.profiles`**. Sistem tidak mencari daftar biasa, ia mencari objek dengan ID spesifik yang memiliki properti `provider` dan `key`. 
Saya menyuntikkan profil siluman:
```json
"profiles": {
  "openai-main": {
    "provider": "openai",
    "key": "nex-niflo-secret",
    "token": "..."
  }
}
```
**Hasil**: Gembok terbuka! Error 500 musnah. ✅

---

## Bab 4: Jalur Siluman (The Stealth 404 Gateway)

### Masalah:
Meskipun gembok terbuka, agen masih mencoba menghubungi `127.0.0.1`. Mengapa? Karena di dalam biner, alamat localhost dikunci (Hardcoded) sebagai nilai default.

### Sihir (Resolve):
1.  **Localhost Purge**: Saya melakukan `sed` massal pada ribuan file untuk mengganti `127.0.0.1:11434` menjadi `nex-niflo-agent-ollama:11434`.
2.  **The Double /v1 Mystery**: Inilah temuan hebat kita. Provider `openai` secara otomatis menambahkan `/v1` di akhir URL. Jika kita menulis `.../v1` di konfigurasi, jalurnya menjadi `.../v1/v1` (Error 404). 
**Tindakan**: Saya menghapus akhiran `/v1` di konfigurasi agar sistem bisa melengkapinya secara otomatis menjadi jalur yang sah.

---

## Bab 5: Purifikasi Pikiran (Fixing 404 Content)

### Masalah:
Koneksi sudah 200 OK, tapi jawaban AI tetap "404". Kok bisa?
**Temuan**: Sistem memiliki fitur **Failover**. Jika ia merasa jalur utama (Ollama) agak lambat, ia akan mencoba melompat ke jalur cadangan (seperti `codex` milik cloud). Karena jalur cadangan itu tidak punya internet, ia menjawab dengan teks "404".

### Sihir (Resolve):
Saya melakukan **Models Purge**. Saya menghapus semua provider cloud dari `models.json`. 
**Logikanya**: Jangan beri sistem pilihan lain. Paksa dia hanya melihat Ollama lokal. Jika tidak ada jalur pelarian, sistem akan dipaksa menunggu hingga otak lokal kita siap menjawab.

---

## Bab 6: Guardrail Layer (The 'int' object Fix)

### Masalah:
Tiba-tiba muncul error Python: `'int' object has no attribute 'get'`.
**Analisa**: Ini terjadi karena AI (Ollama) menjawab dengan angka murni (seperti `404`). Fungsi `json.loads()` mengubah teks "404" menjadi angka `404`. Ketika skrip kita mencoba melakukan `.get()` pada angka tersebut, terjadilah kecelakaan kode.

### Sihir (Resolve):
Saya memperkuat fungsi `safe_parse` di `nex-api/main.py`.
**Logikanya**: Saya menambahkan pengecekan `isinstance(result, dict)`. Jika hasilnya bukan folder (dictionary), bungkus hasilnya ke dalam format yang aman. Ini adalah "Sabuk Pengaman" agar Jembatan API tidak akan pernah mati hanya karena AI memberikan jawaban yang aneh.

---

## Ringkasan Konfigurasi Rahasia (The Sovereign Stack)

Jika Anda ingin membangun ini dari awal, inilah konfigurasi "Sakti"-nya:

### 1. Jembatan API (`nex-api/main.py`)
Minta model dengan label `openclaw`. Ini adalah label netral yang bisa diterima oleh semua pihak.

### 2. Peta Model (`models.json`)
```json
"openai": {
  "baseUrl": "http://nex-niflo-agent-ollama:11434",
  "api": "openai",
  "apiKey": "nex-niflo-secret"
}
```
> [!TIP]
> **RAHASIA**: Jangan tambahkan `/v1` di `baseUrl` untuk provider tipe `openai`, karena sistem akan menambahkannya secara otomatis.

### 3. Kunci Gembok (`auth-profiles.json`)
Gunakan struktur `"profiles": { "ID": { ... } }` untuk memastikan identitas diterima oleh biner.

---

## Penutup: Pelajaran untuk Masa Depan
Menjalankan AI Stack secara lokal bukan hanya soal menjalankan Docker Compose. Ini adalah soal **Harmonisasi Protokol**. Kita harus memahami bagaimana data mengalir di dalam "Saraf" (Biner) dan memastikan tidak ada sumbatan di setiap persimpangan jalan.

**Kedaulatan adalah Hak Anda. Selamat Membangun!** 🚀💎🏁
