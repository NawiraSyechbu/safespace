"""
Semua endpoint REST SafeSpace.
File ini hanya "membungkus" fungsi di backend/services/ menjadi HTTP API.
"""
import os
import sys
from contextlib import contextmanager

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func

from backend.api.deps import get_current_user, require_admin, require_moderator
from backend.api.security import create_token
from backend.database.connection import SessionLocal
from backend.models.appeal import Appeal
from backend.models.comment import Comment
from backend.models.community import Community
from backend.models.moderation_action import ModerationAction
from backend.models.post import Post
from backend.models.prediction import AIPrediction
from backend.models.report import Report
from backend.models.user import User
from backend.schemas.requests import (
    AppealDecisionIn,
    AppealIn,
    CommentIn,
    CommunityIn,
    LoginIn,
    PostIn,
    RegisterIn,
    ReportIn,
    ResolveReportIn,
    ReviewIn,
    RoleIn,
    UsernameIn,
)
from backend.services.admin_service import (
    get_dashboard_statistics,
    update_user_role,
)
from backend.services.appeal_service import (
    create_appeal,
    get_appeals,
    review_appeal,
)
from backend.services.auth_service import login_user, register_user
from backend.services.comment_service import add_comment, get_comments
from backend.services.community_service import (
    create_community,
    get_user_communities,
    join_community,
    list_communities,
)
from backend.services.history_service import get_moderation_history
from backend.services.moderation_service import (
    get_pending_content,
    resolve_report,
    review_content,
)
from backend.services.post_service import create_post, get_feed, get_post
from backend.services.delete_service import delete_content
from backend.services.report_service import create_report, get_reports
from backend.services.user_service import update_username

router = APIRouter(prefix="/api")


# ======================================================================
# Helper
# ======================================================================

@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _check(result):
    """Ubah hasil {"success": False, ...} dari service menjadi error HTTP."""
    if isinstance(result, dict) and result.get("success") is False:
        message = result.get("message") or "Permintaan gagal."
        if result.get("error"):
            raise HTTPException(500, f"{message} ({result['error']})")
        raise HTTPException(400, message)
    return result


def _content_model(content_type: str):
    if content_type == "post":
        return Post
    if content_type == "comment":
        return Comment
    raise HTTPException(400, "Jenis konten tidak valid.")


def _usernames(db, user_ids):
    ids = {i for i in user_ids if i is not None}
    if not ids:
        return {}
    rows = db.query(User.id, User.username).filter(User.id.in_(ids)).all()
    return {row.id: row.username for row in rows}


def _latest_reason(db, content_type, content_id):
    action = (
        db.query(ModerationAction)
        .filter(
            ModerationAction.content_type == content_type,
            ModerationAction.content_id == content_id,
        )
        .order_by(desc(ModerationAction.id))
        .first()
    )
    return action.notes if action else None


def _ai_summary(db, content_type, content_id):
    rows = (
        db.query(AIPrediction)
        .filter(
            AIPrediction.content_type == content_type,
            AIPrediction.content_id == content_id,
        )
        .order_by(AIPrediction.id)
        .all()
    )
    summary = []
    for row in rows:
        probs = row.probabilities or {}
        labels = row.predicted_labels
        if labels is None and probs:
            labels = [max(probs, key=probs.get)]
        summary.append(
            {
                "task": row.task_name,
                "labels": labels or [],
                "scores": {k: round(float(v), 3) for k, v in probs.items()},
            }
        )
    return summary

def _ai1_scores(db, content_type, content_id):
    row = (
        db.query(AIPrediction)
        .filter(
            AIPrediction.content_type == content_type,
            AIPrediction.content_id == content_id,
            AIPrediction.task_name == "ai1_deteksi",
        )
        .order_by(desc(AIPrediction.id))
        .first()
    )
    if not row or not row.probabilities:
        return None

    thresholds = {}
    try:
        from ai.model_config import load_label_config

        config = load_label_config("ai1_deteksi")
        labels = config["labels"]
        raw = config.get("thresholds")
        if isinstance(raw, dict):
            thresholds = {l: float(raw[l]) for l in labels}
        elif isinstance(raw, list):
            thresholds = {l: float(raw[i]) for i, l in enumerate(labels)}
    except Exception:
        pass

    return {
        "scores": {k: float(v) for k, v in row.probabilities.items()},
        "thresholds": thresholds,
    }

def _content_info(db, content_type, content_id):
    model = _content_model(content_type)
    item = db.query(model).filter(model.id == content_id).first()
    if not item:
        return None
    return {
        "content_type": content_type,
        "content_id": item.id,
        "title": getattr(item, "title", None),
        "content": item.content,
        "status": item.moderation_status,
        "user_id": item.user_id,
    }


def _enrich_posts(posts):
    if not posts:
        return posts
    with db_session() as db:
        names = _usernames(db, [p["user_id"] for p in posts])
        comm_rows = db.query(Community.id, Community.name).all()
        comm_names = {row.id: row.name for row in comm_rows}
        counts = dict(
            db.query(Comment.post_id, func.count(Comment.id))
            .filter(
                Comment.post_id.in_([p["id"] for p in posts]),
                Comment.moderation_status == "approved",
            )
            .group_by(Comment.post_id)
            .all()
        )
    for p in posts:
        p["username"] = names.get(p["user_id"], "unknown")
        p["community_name"] = comm_names.get(p["community_id"], "-")
        p["comment_count"] = counts.get(p["id"], 0)
    return posts


# ======================================================================
# Health
# ======================================================================

@router.get("/health")
def health():
    from ai.model_config import MODEL_PATHS

    loader = sys.modules.get("ai.model_loader")
    loaded = set(getattr(loader, "MODEL_CACHE", {}).keys()) if loader else set()

    return {
        "status": "ok",
        "ai_mode": os.getenv("AI_MODE", "real"),
        "models": {
            name: {
                "folder_exists": path.exists(),
                "label_config_exists": (path / "label_config.json").exists(),
                "loaded": name in loaded,
            }
            for name, path in MODEL_PATHS.items()
        },
    }


# ======================================================================
# Auth & user
# ======================================================================

@router.post("/auth/register", status_code=201)
def register(body: RegisterIn):
    result = _check(register_user(body.username, body.email, body.password))
    user = result["user"]
    return {"user": user, "token": create_token(user["id"])}


@router.post("/auth/login")
def login(body: LoginIn):
    result = login_user(body.email, body.password)
    if not result.get("success"):
        raise HTTPException(401, result.get("message", "Email atau password salah."))
    user = result["user"]
    return {"user": user, "token": create_token(user["id"])}


@router.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return user


@router.patch("/users/me")
def change_username(body: UsernameIn, user: dict = Depends(get_current_user)):
    return _check(update_username(user["id"], body.username))


# ======================================================================
# Communities
# ======================================================================

@router.get("/communities")
def communities():
    return list_communities()


@router.post("/communities", status_code=201)
def new_community(body: CommunityIn, user: dict = Depends(require_admin)):
    return _check(create_community(body.name, body.description))


@router.post("/communities/{community_id}/join")
def join(community_id: int, user: dict = Depends(get_current_user)):
    return _check(join_community(user["id"], community_id))


@router.get("/me/communities")
def my_communities(user: dict = Depends(get_current_user)):
    return get_user_communities(user["id"])


# ======================================================================
# Posts & comments
# ======================================================================

@router.get("/posts")
def feed(community_id: int | None = None, limit: int = 30):
    limit = max(1, min(limit, 100))
    return _enrich_posts(get_feed(community_id, limit))


@router.get("/posts/{post_id}")
def post_detail(post_id: int):
    post = get_post(post_id)
    if not post:
        raise HTTPException(404, "Postingan tidak ditemukan.")
    return _enrich_posts([post])[0]


@router.post("/posts", status_code=201)
def new_post(body: PostIn, user: dict = Depends(get_current_user)):
    result = _check(
        create_post(user["id"], body.community_id, body.title, body.content)
    )
    with db_session() as db:
        result["reason"] = _latest_reason(db, "post", result["post_id"])
    return result

def _delete(content_type, content_id, user):
    result = delete_content(user, content_type, content_id)
    if result.get("forbidden"):
        raise HTTPException(403, result["message"])
    return _check(result)


@router.delete("/posts/{post_id}")
def remove_post(post_id: int, user: dict = Depends(get_current_user)):
    return _delete("post", post_id, user)


@router.delete("/comments/{comment_id}")
def remove_comment(comment_id: int, user: dict = Depends(get_current_user)):
    return _delete("comment", comment_id, user)

@router.get("/posts/{post_id}/comments")
def post_comments(post_id: int):
    items = get_comments(post_id)
    with db_session() as db:
        names = _usernames(db, [c["user_id"] for c in items])
    for c in items:
        c["username"] = names.get(c["user_id"], "unknown")
    # urutkan dari yang terlama agar thread mudah dibaca
    items.sort(key=lambda c: c["created_at"])
    return items


@router.post("/posts/{post_id}/comments", status_code=201)
def new_comment(post_id: int, body: CommentIn, user: dict = Depends(get_current_user)):
    result = _check(
        add_comment(user["id"], post_id, body.content, body.parent_comment_id)
    )
    with db_session() as db:
        result["reason"] = _latest_reason(db, "comment", result["comment_id"])
    return result


# ======================================================================
# Laporan & banding (sisi pengguna)
# ======================================================================

@router.post("/reports", status_code=201)
def report(body: ReportIn, user: dict = Depends(get_current_user)):
    return _check(
        create_report(user["id"], body.content_type, body.content_id, body.reason)
    )


@router.post("/appeals", status_code=201)
def appeal(body: AppealIn, user: dict = Depends(get_current_user)):
    return _check(
        create_appeal(user["id"], body.content_type, body.content_id, body.reason)
    )


@router.get("/me/content")
def my_content(user: dict = Depends(get_current_user)):
    """Semua postingan & komentar milik pengguna beserta status moderasinya."""
    uid = user["id"]
    items = []

    with db_session() as db:
        posts = (
            db.query(Post).filter(Post.user_id == uid)
            .order_by(desc(Post.created_at)).limit(50).all()
        )
        comments = (
            db.query(Comment).filter(Comment.user_id == uid)
            .order_by(desc(Comment.created_at)).limit(50).all()
        )
        appeals = (
            db.query(Appeal).filter(Appeal.user_id == uid)
            .order_by(Appeal.id.asc()).all()
        )
        appeal_status = {(a.content_type, a.content_id): a.status for a in appeals}

        for ctype, rows in (("post", posts), ("comment", comments)):
            for row in rows:
                items.append(
                    {
                        "content_type": ctype,
                        "content_id": row.id,
                        "post_id": row.id if ctype == "post" else row.post_id,
                        "title": getattr(row, "title", None),
                        "content": row.content,
                        "status": row.moderation_status,
                        "reason": (
                            _latest_reason(db, ctype, row.id)
                            if row.moderation_status != "approved" else None
                        ),
                        "ai": (
                            _ai1_scores(db, ctype, row.id)
                            if row.moderation_status != "approved" else None
                        ),
                        "appeal_status": appeal_status.get((ctype, row.id)),
                        "created_at": row.created_at,
                    }
                )

    items.sort(key=lambda i: i["created_at"], reverse=True)
    return items


# ======================================================================
# Moderasi (moderator & admin)
# ======================================================================

@router.get("/moderation/pending")
def pending(user: dict = Depends(require_moderator)):
    items = get_pending_content()
    with db_session() as db:
        names = _usernames(db, [i["user_id"] for i in items])
        for item in items:
            item["username"] = names.get(item["user_id"], "unknown")
            item["reason"] = _latest_reason(db, item["type"], item["id"])
            item["ai"] = _ai_summary(db, item["type"], item["id"])
    items.sort(key=lambda i: i["created_at"])
    return items


@router.post("/moderation/review")
def review(body: ReviewIn, user: dict = Depends(require_moderator)):
    return _check(
        review_content(
            user["id"], body.content_type, body.content_id,
            body.new_status, body.notes,
        )
    )


@router.get("/moderation/reports")
def reports(user: dict = Depends(require_moderator)):
    items = [r for r in get_reports() if r["status"] == "pending"]
    with db_session() as db:
        names = _usernames(db, [r["reporter_id"] for r in items])
        for r in items:
            r["reporter"] = names.get(r["reporter_id"], "unknown")
            r["target"] = _content_info(db, r["content_type"], r["content_id"])
    return items


@router.post("/moderation/reports/{report_id}/resolve")
def resolve(report_id: int, body: ResolveReportIn, user: dict = Depends(require_moderator)):
    return _check(resolve_report(report_id, user["id"], body.action, body.notes))


@router.get("/moderation/appeals")
def appeals(user: dict = Depends(require_moderator)):
    items = get_appeals("pending")
    with db_session() as db:
        names = _usernames(db, [a["user_id"] for a in items])
        for a in items:
            a["username"] = names.get(a["user_id"], "unknown")
            a["target"] = _content_info(db, a["content_type"], a["content_id"])
            a["ai_reason"] = _latest_reason(db, a["content_type"], a["content_id"])
            a["ai"] = _ai_summary(db, a["content_type"], a["content_id"])
    return items


@router.post("/moderation/appeals/{appeal_id}/review")
def decide_appeal(appeal_id: int, body: AppealDecisionIn, user: dict = Depends(require_moderator)):
    return _check(review_appeal(appeal_id, user["id"], body.decision))


@router.get("/moderation/history/{content_type}/{content_id}")
def history(content_type: str, content_id: int, user: dict = Depends(require_moderator)):
    _content_model(content_type)
    return get_moderation_history(content_type, content_id)


# ======================================================================
# Admin
# ======================================================================

@router.get("/admin/stats")
def stats(user: dict = Depends(require_admin)):
    data = get_dashboard_statistics()

    with db_session() as db:
        def by_status(model):
            rows = (
                db.query(model.moderation_status, func.count(model.id))
                .group_by(model.moderation_status).all()
            )
            return {status: count for status, count in rows}

        data["posts_by_status"] = by_status(Post)
        data["comments_by_status"] = by_status(Comment)
        data["total_predictions"] = db.query(AIPrediction).count()
        data["open_reports"] = db.query(Report).filter(Report.status == "pending").count()
        data["open_appeals"] = db.query(Appeal).filter(Appeal.status == "pending").count()

    return data


@router.get("/admin/users")
def users(user: dict = Depends(require_admin)):
    with db_session() as db:
        rows = db.query(User).order_by(User.id.asc()).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "created_at": u.created_at,
            }
            for u in rows
        ]


@router.patch("/admin/users/{user_id}/role")
def change_role(user_id: int, body: RoleIn, user: dict = Depends(require_admin)):
    if user_id == user["id"]:
        raise HTTPException(400, "Kamu tidak bisa mengubah role akunmu sendiri.")
    return _check(update_user_role(user_id, body.role))
