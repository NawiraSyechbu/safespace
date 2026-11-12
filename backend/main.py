"""
Titik masuk aplikasi SafeSpace.

Jalankan dari folder utama proyek:
    uvicorn backend.main:app --port 8000
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", encoding="utf-8-sig")

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.api.routes import router  # noqa: E402

log = logging.getLogger("safespace")
DIST_DIR = ROOT_DIR / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Buat tabel database & isi komunitas awal (aman dijalankan berulang)
    from backend.database.db_init import init_database
    from scripts.seed_data import seed_communities

    init_database()
    seed_communities()

    # 2. Muat model AI saat server menyala agar request pertama tidak lambat
    mode = os.getenv("AI_MODE", "real").lower()
    if mode == "mock":
        log.warning("AI_MODE=mock: yang dipakai BUKAN model AI asli (hanya untuk uji alur).")
    elif os.getenv("AI_PRELOAD", "1") == "1":
        try:
            from ai.model_loader import load_all_models

            load_all_models()
            log.info("Ketiga model AI berhasil dimuat.")
        except Exception as error:
            log.warning(
                "Model AI gagal dimuat: %s. Konten baru akan masuk antrean "
                "moderator (pending_review) sampai model tersedia.", error,
            )

    yield


app = FastAPI(title="SafeSpace API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
        if o.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    fields = ", ".join(
        str(e["loc"][-1]) for e in exc.errors() if e.get("loc")
    )
    return JSONResponse(
        status_code=422,
        content={"detail": f"Data yang dikirim tidak valid ({fields})."},
    )


app.include_router(router)


# Jika frontend sudah di-build (frontend/dist), tampilkan lewat server yang sama
if DIST_DIR.exists():
    if (DIST_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(404, "Endpoint tidak ditemukan.")

        candidate = (DIST_DIR / full_path).resolve()
        if full_path and candidate.is_file() and DIST_DIR.resolve() in candidate.parents:
            return FileResponse(candidate)

        return FileResponse(DIST_DIR / "index.html")
