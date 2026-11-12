"""Token login sederhana (HMAC-SHA256) tanpa library tambahan."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _secret() -> bytes:
    key = os.getenv("SECRET_KEY")
    if key:
        return key.encode("utf-8")

    # Jika SECRET_KEY tidak diisi di .env, buat otomatis sekali lalu simpan.
    key_file = ROOT_DIR / "data" / ".secret_key"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32), encoding="utf-8")
    return key_file.read_text(encoding="utf-8").strip().encode("utf-8")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def create_token(user_id: int) -> str:
    ttl = int(os.getenv("TOKEN_EXPIRE_HOURS", "72")) * 3600
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + ttl}).encode())
    sig = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def decode_token(token: str):
    """Mengembalikan user_id, atau None jika token tidak valid/kedaluwarsa."""
    try:
        payload, sig = token.split(".")
        expected = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(_unb64(payload))
        if data["exp"] < time.time():
            return None
        return int(data["uid"])
    except Exception:
        return None
