# SafeSpace – Cara Menjalankan (Backend + Frontend + Model AI)

Semua jalan di **satu alamat: http://localhost:8000** (FastAPI melayani API dan website React sekaligus).

## 0. Prasyarat
- Python 3.11 (sesuai venv-mu), Node.js 20.19+ atau 22.12+ (cek: `node -v`)

## 1. Kembalikan model AI
Salin 3 folder model ke `ai/saved_model/`, struktur harus persis:

```
ai/saved_model/
  model_ai1_deteksi/    (config.json, model.safetensors, tokenizer*, label_config.json)
  model_ai2_kategori/   (idem)
  model_ai2_level/      (idem)
```
Tiap folder wajib berisi `label_config.json`. Cek dulu modelnya jalan:
```
python scripts/test_ai.py
```

## 2. Jalankan (Windows)
Klik dua kali `start.bat` atau di terminal:
```
start.bat
```
Pertama kali ia otomatis: install dependensi frontend, build React, lalu menyalakan server.
Tunggu sampai muncul `Application startup complete`, lalu buka **http://localhost:8000**.

Mac/Linux: `./start.sh`

## 3. Jadikan akunmu admin / moderator
1. Daftar lewat website (menu Get started).
2. Di terminal baru (venv aktif):
```
python scripts/create_admin.py emailkamu@contoh.com admin
python scripts/create_admin.py email_teman@contoh.com moderator
```
3. Log out lalu log in lagi. Menu **Moderasi** dan **Admin** akan muncul.

## 4. Cek status
- http://localhost:8000/api/health  -> menunjukkan apakah ketiga model ditemukan & termuat.
- http://localhost:8000/docs        -> dokumentasi API interaktif.

## Mode pengembangan frontend (opsional, hot reload)
Terminal 1: `python -m uvicorn backend.main:app --reload --port 8000`
Terminal 2: `cd frontend && npm run dev`  -> buka http://localhost:5173
(Jika mengubah kode React dan memakai start.bat, hapus folder `frontend/dist` agar di-build ulang.)

## Tes alur web tanpa model (hanya untuk uji)
Di `.env` ubah `AI_MODE=mock`. Teks berisi `[uji-blokir]` -> ditolak, `[uji-review]` -> masuk antrean
moderator, selain itu disetujui. Ini BUKAN model AI; kembalikan ke `AI_MODE=real` untuk demo.
