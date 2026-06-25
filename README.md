# 🔍 OSINT Username Checker

Cek keberadaan sebuah username di **45+ platform** sosial media & developer tools secara paralel, pakai Python `async` + `httpx`.

Tersedia dalam 3 bentuk: **Web App Streamlit** (siap deploy), **Web App FastAPI** (lokal), dan **CLI**.

---

## ✨ Fitur

- ⚡ **Async paralel** — scan puluhan platform dalam hitungan detik.
- 🎯 **Deteksi 4 status** — `found`, `not found`, `blocked` (diblokir/ragu), `error`.
- 🟢 **Hasil live** — muncul satu per satu saat tiap platform selesai dicek.
- 🗂️ **Grouping per kategori** + filter + badge warna.
- ⬇️ **Export** — download JSON & copy semua URL sekali klik.
- 🇮🇩 Sudah termasuk platform lokal (Tokopedia, Shopee, Kaskus).

---

## 📦 Install

```bash
pip install -r requirements.txt
```

> Butuh Python 3.10+.

---

## 🚀 Cara Pakai

### 1. Streamlit (paling gampang, bisa di-deploy online)

```bash
streamlit run streamlit_app.py
```

Buka **http://localhost:8501**.

### 2. Web App FastAPI (lokal)

```bash
python web.py
```

Buka **http://127.0.0.1:8000**.

### 3. CLI

```bash
python main.py check johndoe                  # cek username
python main.py check johndoe --only-found     # hanya yang ditemukan
python main.py check johndoe --output hasil.json
python main.py check johndoe --report         # generate HTML report
python main.py check johndoe -c 30 -t 8       # concurrency 30, timeout 8s
python main.py platforms                       # list semua platform
```

---

## ☁️ Deploy ke Streamlit Community Cloud (streamlit.app)

Gratis & permanen. Langkah:

1. Pastikan repo ini sudah ada di GitHub (public).
2. Buka **<https://share.streamlit.io>** → login dengan akun GitHub.
3. Klik **"Create app"** → **"Deploy a public app from GitHub"**.
4. Isi:
   - **Repository:** `akbarfdlh2/Username-OSINT-Tool`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
5. Klik **Deploy**. Tunggu ±2 menit — app langsung online di URL `https://<nama>.streamlit.app`.

Streamlit Cloud otomatis baca `requirements.txt` untuk install dependency, dan auto-redeploy tiap kali kamu `git push` ke `main`.

---

## ➕ Tambah Platform Baru

Edit [`osint/platforms.py`](osint/platforms.py):

```python
"NamaPlatform": {
    "url": "https://platform.com/{}",   # {} = username
    "category": "Social",
    "check": "status_code",             # atau "content"
},
```

Untuk platform yang balas HTTP 200 walau user tidak ada, pakai content check:

```python
"Platform": {
    "url": "https://platform.com/profile/{}",
    "category": "Forum",
    "check": "content",
    "content_absent": "User not found",  # teks ini muncul = user TIDAK ada
},
```

---

## 🗂️ Struktur Project

```
Username-OSINT-Tool/
├── streamlit_app.py     # Web app Streamlit (untuk deploy)
├── web.py               # Web app FastAPI (lokal)
├── main.py              # CLI (Typer)
├── requirements.txt
└── osint/
    ├── checker.py       # Async HTTP checker (httpx + semaphore)
    ├── platforms.py     # Daftar 45+ platform
    └── reporter.py      # HTML report generator
```

---

## ⚠️ Disclaimer

Tool ini untuk keperluan **edukasi & riset OSINT**. Hasil "ditemukan" bisa saja _false-positive_ (beberapa platform balas HTTP 200 walau user tidak ada) — verifikasi manual lewat link. Gunakan secara bertanggung jawab.

---

Created by **[Akbar Fadilah](https://muhamadakbarfadilah.my.id/)** · Founder & Co-Founder at **[Afda Technology Solutions](https://afdatech.com/)**
