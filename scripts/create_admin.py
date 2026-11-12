"""
Mengubah role akun yang sudah terdaftar.

Contoh:
    python scripts/create_admin.py email@kamu.com admin
    python scripts/create_admin.py email@kamu.com moderator
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.database.connection import SessionLocal  # noqa: E402
from backend.models.user import User  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("Pemakaian: python scripts/create_admin.py <email> [admin|moderator|user]")
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    role = sys.argv[2] if len(sys.argv) > 2 else "admin"

    if role not in ("user", "moderator", "admin"):
        print("Role harus: user, moderator, atau admin.")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Akun dengan email {email} tidak ditemukan. Daftar dulu lewat website.")
            sys.exit(1)
        user.role = role
        db.commit()
        print(f"Berhasil: {user.username} ({email}) sekarang berperan sebagai {role}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
