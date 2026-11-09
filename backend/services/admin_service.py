
from backend.database.connection import SessionLocal
from backend.models.user import User
from backend.models.post import Post
from backend.models.comment import Comment
from backend.models.report import Report


def get_dashboard_statistics():
    db = SessionLocal()

    try:
        return {
            "total_users": db.query(User).count(),
            "total_posts": db.query(Post).count(),
            "total_comments": db.query(Comment).count(),
            "total_reports": db.query(Report).count(),
            "pending_posts": db.query(Post).filter(
                Post.moderation_status == "pending_review"
            ).count(),
            "pending_comments": db.query(Comment).filter(
                Comment.moderation_status == "pending_review"
            ).count()
        }

    finally:
        db.close()


def update_user_role(user_id, new_role):
    if new_role not in ["user", "moderator", "admin"]:
        return {"success": False, "message": "Role tidak valid."}

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"success": False, "message": "Pengguna tidak ditemukan."}

        user.role = new_role
        db.commit()

        return {"success": True, "message": "Role berhasil diperbarui."}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
