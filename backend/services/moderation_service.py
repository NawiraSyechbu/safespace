
from backend.database.connection import SessionLocal
from backend.models.post import Post
from backend.models.comment import Comment
from backend.models.moderation_action import ModerationAction


def review_content(
    moderator_id,
    content_type,
    content_id,
    new_status,
    notes=None
):
    if content_type not in ["post", "comment"]:
        return {"success": False, "message": "Jenis konten tidak valid."}

    if new_status not in ["approved", "blocked"]:
        return {"success": False, "message": "Keputusan tidak valid."}

    db = SessionLocal()

    try:
        model = Post if content_type == "post" else Comment

        content = (
            db.query(model)
            .filter(model.id == content_id)
            .first()
        )

        if not content:
            return {"success": False, "message": "Konten tidak ditemukan."}

        if content.moderation_status != "pending_review":
            return {
                "success": False,
                "message": "Konten tidak sedang menunggu peninjauan."
            }

        content.moderation_status = new_status

        db.add(
            ModerationAction(
                moderator_id=moderator_id,
                content_type=content_type,
                content_id=content_id,
                action=new_status,
                notes=notes
            )
        )

        db.commit()

        return {
            "success": True,
            "message": "Keputusan moderasi berhasil disimpan."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_pending_content():
    db = SessionLocal()

    try:
        posts = (
            db.query(Post)
            .filter(Post.moderation_status == "pending_review")
            .all()
        )

        comments = (
            db.query(Comment)
            .filter(Comment.moderation_status == "pending_review")
            .all()
        )

        result = []

        for post in posts:
            result.append({
                "id": post.id,
                "type": "post",
                "title": post.title,
                "content": post.content,
                "user_id": post.user_id,
                "created_at": post.created_at
            })

        for comment in comments:
            result.append({
                "id": comment.id,
                "type": "comment",
                "title": None,
                "content": comment.content,
                "user_id": comment.user_id,
                "created_at": comment.created_at
            })

        return result

    finally:
        db.close()
