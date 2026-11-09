
import re
import bcrypt

from sqlalchemy.exc import IntegrityError

from backend.database.connection import SessionLocal
from backend.models.user import User


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, password_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3 or len(username) > 50:
        return {
            "success": False,
            "message": "Username harus terdiri dari 3–50 karakter."
        }

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return {
            "success": False,
            "message": "Format email tidak valid."
        }

    if len(password) < 8:
        return {
            "success": False,
            "message": "Password minimal 8 karakter."
        }

    db = SessionLocal()

    try:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="user"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Registrasi berhasil.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }

    except IntegrityError:
        db.rollback()

        return {
            "success": False,
            "message": "Username atau email sudah digunakan."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def login_user(email, password):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email.strip().lower())
            .first()
        )

        if not user or not verify_password(
            password,
            user.password_hash
        ):
            return {
                "success": False,
                "message": "Email atau password salah."
            }

        return {
            "success": True,
            "message": "Login berhasil.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }

    finally:
        db.close()
