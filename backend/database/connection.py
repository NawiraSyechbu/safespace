
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker


# Menentukan root folder proyek
ROOT_DIR = Path(__file__).resolve().parents[2]

# Folder penyimpanan database
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Lokasi database SQLite
DATABASE_URL = f"sqlite:///{(DATA_DIR / 'safespace.db').as_posix()}"


# Membuat engine database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


# Mengaktifkan foreign key SQLite
@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session database
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


# Base untuk seluruh model ORM
Base = declarative_base()


# Fungsi mendapatkan session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
