@echo off
setlocal
cd /d "%~dp0"

echo ==== SafeSpace ====

if not exist venv\Scripts\activate.bat (
    echo [1/4] Membuat virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

if not exist frontend\node_modules (
    echo [2/4] Menginstal dependensi frontend...
    pushd frontend
    call npm install
    popd
)

if not exist frontend\dist\index.html (
    echo [3/4] Membangun frontend...
    pushd frontend
    call npm run build
    popd
)

echo [4/4] Menjalankan server di http://localhost:8000
echo (Tunggu sampai muncul "Application startup complete", lalu buka alamat di atas)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
