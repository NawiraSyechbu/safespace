
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.database.connection import SessionLocal
from backend.models.community import Community


INITIAL_COMMUNITIES = [
    {
        "name": "General Discussion",
        "description": "Tempat berdiskusi mengenai berbagai topik umum."
    },
    {
        "name": "Technology",
        "description": "Diskusi seputar teknologi, AI, dan perkembangan digital."
    },
    {
        "name": "Education",
        "description": "Ruang berbagi informasi dan pengalaman pendidikan."
    },
    {
        "name": "Mental Wellness",
        "description": "Tempat berbagi cerita dan saling memberikan dukungan."
    },
]


def seed_communities():
    db = SessionLocal()

    try:
        for item in INITIAL_COMMUNITIES:
            existing = (
                db.query(Community)
                .filter(Community.name == item["name"])
                .first()
            )

            if not existing:
                db.add(Community(**item))

        db.commit()
        print("Data komunitas awal berhasil dimasukkan.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_communities()