
from backend.database.connection import SessionLocal
from backend.models.report import Report
from backend.models.post import Post
from backend.models.comment import Comment


def create_report(reporter_id, content_type, content_id, reason):
    if content_type not in ["post", "comment"]:
        return {"success": False, "message": "Jenis konten tidak valid."}

    if not reason.strip():
        return {"success": False, "message": "Alasan laporan wajib diisi."}

    db = SessionLocal()

    try:
        model = Post if content_type == "post" else Comment

        content = db.query(model).filter(model.id == content_id).first()

        if not content:
            return {"success": False, "message": "Konten tidak ditemukan."}

        report = Report(
            reporter_id=reporter_id,
            content_type=content_type,
            content_id=content_id,
            reason=reason.strip()
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "success": True,
            "report_id": report.id,
            "message": "Laporan berhasil dikirim."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_reports():
    db = SessionLocal()

    try:
        reports = (
            db.query(Report)
            .order_by(Report.created_at.desc())
            .all()
        )

        return [
            {
                "id": item.id,
                "reporter_id": item.reporter_id,
                "content_type": item.content_type,
                "content_id": item.content_id,
                "reason": item.reason,
                "status": item.status,
                "created_at": item.created_at
            }
            for item in reports
        ]

    finally:
        db.close()
