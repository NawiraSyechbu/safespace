
from backend.database.connection import SessionLocal
from backend.models.appeal import Appeal
from backend.models.post import Post
from backend.models.comment import Comment


def create_appeal(user_id, content_type, content_id, reason):
    if content_type not in ["post", "comment"]:
        return {"success": False, "message": "Jenis konten tidak valid."}

    if not reason.strip():
        return {"success": False, "message": "Alasan banding wajib diisi."}

    db = SessionLocal()

    try:
        model = Post if content_type == "post" else Comment

        content = (
            db.query(model)
            .filter(
                model.id == content_id,
                model.user_id == user_id,
                model.moderation_status == "blocked"
            )
            .first()
        )

        if not content:
            return {
                "success": False,
                "message": "Konten tidak ditemukan atau tidak memenuhi syarat banding."
            }

        existing = (
            db.query(Appeal)
            .filter(
                Appeal.user_id == user_id,
                Appeal.content_type == content_type,
                Appeal.content_id == content_id,
                Appeal.status == "pending"
            )
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "Banding untuk konten ini masih diproses."
            }

        appeal = Appeal(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            reason=reason.strip()
        )

        db.add(appeal)
        db.commit()
        db.refresh(appeal)

        return {
            "success": True,
            "appeal_id": appeal.id,
            "message": "Pengajuan banding berhasil dikirim."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def review_appeal(appeal_id, moderator_id, decision):
    if decision not in ["accepted", "rejected"]:
        return {"success": False, "message": "Keputusan banding tidak valid."}

    db = SessionLocal()

    try:
        appeal = (
            db.query(Appeal)
            .filter(Appeal.id == appeal_id)
            .first()
        )

        if not appeal or appeal.status != "pending":
            return {
                "success": False,
                "message": "Pengajuan banding tidak ditemukan atau sudah diproses."
            }

        model = Post if appeal.content_type == "post" else Comment

        content = (
            db.query(model)
            .filter(model.id == appeal.content_id)
            .first()
        )

        if not content:
            return {"success": False, "message": "Konten tidak ditemukan."}

        appeal.status = decision
        appeal.reviewed_by = moderator_id

        if decision == "accepted":
            content.moderation_status = "approved"

        db.commit()

        return {
            "success": True,
            "message": "Pengajuan banding berhasil diproses."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
