
from backend.database.connection import SessionLocal
from backend.models.user import User
from backend.models.community import Community


def test_database_connection():
    db = SessionLocal()

    try:
        db.query(User).count()
        db.query(Community).count()

        print("Koneksi database berhasil.")

    finally:
        db.close()


if __name__ == "__main__":
    test_database_connection()
