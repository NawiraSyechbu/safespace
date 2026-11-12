
from sqlalchemy import desc

from backend.database.connection import SessionLocal
from backend.models.comment import Comment
from backend.models.post import Post
from backend.models.prediction import AIPrediction
from backend.models.moderation_action import ModerationAction

from ai.moderation_engine import analyze_text


def add_comment(user_id, post_id, content, parent_comment_id=None):
    content = content.strip()

    if not content:
        return {"success": False, "message": "Komentar tidak boleh kosong."}

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
            return {
                "success": False,
                "message": "Postingan tidak ditemukan atau tidak tersedia."
            }

        if parent_comment_id is not None:
            parent = (
                db.query(Comment)
                .filter(
                    Comment.id == parent_comment_id,
                    Comment.post_id == post_id,
                    Comment.moderation_status == "approved"
                )
                .first()
            )

            if not parent:
                return {
                    "success": False,
                    "message": "Komentar yang akan dibalas tidak ditemukan."
                }

        moderation = analyze_text(content)
        status = moderation.get("status", "pending_review")

        if status not in ["approved", "blocked", "pending_review"]:
            status = "pending_review"

        comment = Comment(
            user_id=user_id,
            post_id=post_id,
            parent_comment_id=parent_comment_id,
            content=content,
            moderation_status=status
        )

        db.add(comment)
        db.flush()

        for task_name, result in (moderation.get("predictions") or {}).items():
            if not isinstance(result, dict):
                continue

            db.add(
                AIPrediction(
                    content_type="comment",
                    content_id=comment.id,
                    task_name=task_name,
                    predicted_labels=result.get("predicted_labels")
                    if "predicted_labels" in result
                    else [result.get("predicted_label")],
                    probabilities=result.get("scores"),
                    confidence=str(result.get("confidence"))
                    if result.get("confidence") is not None else None,
                    model_version="indobert-iterasi4"
                )
            )

        db.add(
            ModerationAction(
                moderator_id=None,
                content_type="comment",
                content_id=comment.id,
                action=status,
                notes=moderation.get("reason", "Moderasi otomatis")
            )
        )

        db.commit()
        db.refresh(comment)

        return {
            "success": True,
            "comment_id": comment.id,
            "moderation_status": status,
            "message": {
                "approved": "Komentar berhasil diterbitkan.",
                "blocked": "Komentar ditolak oleh sistem moderasi.",
                "pending_review": "Komentar menunggu peninjauan moderator."
            }[status]
        }

    except Exception as error:
        db.rollback()
        return {
            "success": False,
            "message": "Gagal menambahkan komentar.",
            "error": str(error)
        }

    finally:
        db.close()


def get_comments(post_id):
    db = SessionLocal()

    try:
        comments = (
            db.query(Comment)
            .filter(
                Comment.post_id == post_id,
                Comment.moderation_status == "approved"
            )
            .order_by(desc(Comment.created_at))
            .all()
        )

        return [
            {
                "id": item.id,
                "post_id": item.post_id,
                "user_id": item.user_id,
                "parent_comment_id": item.parent_comment_id,
                "content": item.content,
                "created_at": item.created_at
            }
            for item in comments
        ]

    finally:
        db.close()
