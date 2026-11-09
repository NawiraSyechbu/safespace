
from backend.database.connection import Base, engine
import backend.models


def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database SafeSpace berhasil dibuat.")


if __name__ == "__main__":
    init_database()