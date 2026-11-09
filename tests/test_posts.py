
from backend.database.connection import SessionLocal
from backend.models.user import User
from backend.models.community import Community
from backend.services.post_service import create_post, get_feed


def test_post_workflow():
    db = SessionLocal()

    try:
        user = db.query(User).first()
        community = db.query(Community).first()

        assert user is not None, "Belum ada user di database."
        assert community is not None, "Belum ada komunitas di database."

        user_id = user.id
        community_id = community.id

    finally:
        db.close()

    result = create_post(
        user_id=user_id,
        community_id=community_id,
        title="Diskusi tentang teknologi",
        content="Apa pendapat kalian mengenai perkembangan teknologi AI?"
    )

    print("Hasil pembuatan post:", result)

    feed = get_feed(community_id)
    print("Jumlah postingan yang tampil:", len(feed))


if __name__ == "__main__":
    test_post_workflow()
