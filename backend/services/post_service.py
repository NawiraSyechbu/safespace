
from sqlalchemy import desc

from backend.database.connection import SessionLocal
from backend.models.post import Post
from backend.models.community import Community
from backend.models.prediction import AIPrediction
from backend.models.moderation_action import ModerationAction

from ai.moderation_engine import analyze_text


def save_predictions(db, content_type, content_id, predictions):
    if not predictions:
        return

    for task_name, result in predictions.items():
        if not isinstance(result, dict):
            continue

        db.add(
            AIPrediction(
                content_type=content_type,
                content_id=content_id,
                task_name=task_name,
                predicted_labels=result.get("predicted_labels"),
                probabilities=result.get("scores"),
                confidence=str(result.get("confidence"))
                if result.get("confidence") is not None else None,
                model_version="indobert-iterasi4"
            )
        )


def create_post(user_id, community_id, title, content):
    title = title.strip()
    content = content.strip()

    if not title or not content:
        return {
            "success": False,
            "message": "Judul dan isi postingan wajib diisi."
        }

    if len(title) > 200:
        return {"success": False, "message": "Judul maksimal 200 karakter."}

    db = SessionLocal()

    try:
        community = (
            db.query(Community)
            .filter(Community.id == community_id)
            .first()
        )

        if not community:
            return {"success": False, "message": "Komunitas tidak ditemukan."}

        # Jalankan moderasi sebelum publikasi
        moderation = analyze_text(content)

        status = moderation.get("status", "pending_review")

        # Jika proses AI gagal, konten tetap tidak dipublikasikan
        if status not in ["approved", "blocked", "pending_review"]:
            status = "pending_review"

        post = Post(
            user_id=user_id,
            community_id=community_id,
            title=title,
            content=content,
            moderation_status=status
        )

        db.add(post)
        db.flush()

        save_predictions(
            db,
            "post",
            post.id,
            moderation.get("predictions")
        )

        db.add(
            ModerationAction(
                moderator_id=None,
                content_type="post",
                content_id=post.id,
                action=status,
                notes=moderation.get("reason", "Moderasi otomatis")
            )
        )

        db.commit()
        db.refresh(post)

        messages = {
            "approved": "Postingan berhasil diterbitkan.",
            "blocked": "Postingan ditolak oleh sistem moderasi.",
            "pending_review": "Postingan menunggu peninjauan moderator."
        }

        return {
            "success": True,
            "post_id": post.id,
            "moderation_status": status,
            "message": messages[status]
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "message": "Gagal membuat postingan.",
            "error": str(error)
        }

    finally:
        db.close()


def get_feed(community_id=None, limit=30):
    db = SessionLocal()

    try:
        query = db.query(Post).filter(
            Post.moderation_status == "approved"
        )

        if community_id is not None:
            query = query.filter(Post.community_id == community_id)

        posts = (
            query.order_by(desc(Post.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": post.id,
                "user_id": post.user_id,
                "community_id": post.community_id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at
            }
            for post in posts
        ]

    finally:
        db.close()


def get_post(post_id):
    db = SessionLocal()

    try:
        post = (
            db.query(Post)
            .filter(
                Post.id == post_id,
                Post.moderation_status == "approved"
            )
            .first()
        )

        if not post:
            return None

        return {
            "id": post.id,
            "user_id": post.user_id,
            "community_id": post.community_id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at
        }

    finally:
        db.close()
