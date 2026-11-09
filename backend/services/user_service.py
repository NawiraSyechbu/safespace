
from backend.database.connection import SessionLocal
from backend.models.user import User


def get_user_by_id(user_id):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }

    finally:
        db.close()


def update_username(user_id, new_username):
    new_username = new_username.strip()

    if len(new_username) < 3 or len(new_username) > 50:
        return {
            "success": False,
            "message": "Username harus terdiri dari 3–50 karakter."
        }

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"success": False, "message": "Pengguna tidak ditemukan."}

        duplicate = (
            db.query(User)
            .filter(
                User.username == new_username,
                User.id != user_id
            )
            .first()
        )

        if duplicate:
            return {"success": False, "message": "Username sudah digunakan."}

        user.username = new_username
        db.commit()

        return {"success": True, "message": "Username berhasil diperbarui."}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
