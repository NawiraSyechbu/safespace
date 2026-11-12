from backend.database.connection import SessionLocal
from backend.models.post import Post
from backend.models.comment import Comment
from backend.models.report import Report
from backend.models.appeal import Appeal
from backend.models.prediction import AIPrediction
from backend.models.moderation_action import ModerationAction


def _descendant_comment_ids(db, root_ids):
    all_ids = set(root_ids)
    frontier = list(root_ids)
    while frontier:
        rows = db.query(Comment.id).filter(
            Comment.parent_comment_id.in_(frontier)
        ).all()
        frontier = [r.id for r in rows if r.id not in all_ids]
        all_ids.update(frontier)
    return all_ids


def _purge_related(db, content_type, ids):
    if not ids:
        return
    for model in (Report, Appeal, AIPrediction, ModerationAction):
        db.query(model).filter(
            model.content_type == content_type,
            model.content_id.in_(list(ids)),
        ).delete(synchronize_session=False)


def delete_content(actor, content_type, content_id):
    if content_type not in ("post", "comment"):
        return {"success": False, "message": "Jenis konten tidak valid."}

    model = Post if content_type == "post" else Comment
    db = SessionLocal()

    try:
        item = db.query(model).filter(model.id == content_id).first()

        if not item:
            return {"success": False, "message": "Konten tidak ditemukan."}

        if item.user_id != actor["id"] and actor["role"] not in ("moderator", "admin"):
            return {
                "success": False,
                "forbidden": True,
                "message": "Kamu tidak berhak menghapus konten ini.",
            }

        if content_type == "post":
            comment_ids = {
                r.id for r in db.query(Comment.id)
                .filter(Comment.post_id == content_id).all()
            }
        else:
            comment_ids = _descendant_comment_ids(db, [content_id])

        _purge_related(db, "comment", comment_ids)
        if content_type == "post":
            _purge_related(db, "post", [content_id])

        # Komentar ikut terhapus lewat ON DELETE CASCADE di database
        db.delete(item)
        db.commit()

        return {"success": True, "message": "Konten berhasil dihapus."}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()