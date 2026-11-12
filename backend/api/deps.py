from fastapi import Depends, Header, HTTPException

from backend.api.security import decode_token
from backend.services.user_service import get_user_by_id


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Silakan login terlebih dahulu.")

    user_id = decode_token(authorization[7:].strip())
    if user_id is None:
        raise HTTPException(401, "Sesi login tidak valid atau sudah berakhir.")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(401, "Akun tidak ditemukan.")
    return user


def require_moderator(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("moderator", "admin"):
        raise HTTPException(403, "Hanya moderator atau admin yang dapat mengakses ini.")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(403, "Hanya admin yang dapat mengakses ini.")
    return user
