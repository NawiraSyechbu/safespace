
from sqlalchemy.exc import IntegrityError

from backend.database.connection import SessionLocal
from backend.models.community import Community
from backend.models.community_member import CommunityMember


def list_communities():
    db = SessionLocal()

    try:
        communities = (
            db.query(Community)
            .order_by(Community.name.asc())
            .all()
        )

        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description
            }
            for item in communities
        ]

    finally:
        db.close()


def create_community(name, description):
    name = name.strip()

    if not name:
        return {"success": False, "message": "Nama komunitas wajib diisi."}

    db = SessionLocal()

    try:
        community = Community(
            name=name,
            description=description.strip() if description else None
        )

        db.add(community)
        db.commit()
        db.refresh(community)

        return {
            "success": True,
            "community_id": community.id,
            "message": "Komunitas berhasil dibuat."
        }

    except IntegrityError:
        db.rollback()
        return {"success": False, "message": "Nama komunitas sudah digunakan."}

    finally:
        db.close()


def join_community(user_id, community_id):
    db = SessionLocal()

    try:
        community = (
            db.query(Community)
            .filter(Community.id == community_id)
            .first()
        )

        if not community:
            return {"success": False, "message": "Komunitas tidak ditemukan."}

        existing = (
            db.query(CommunityMember)
            .filter_by(user_id=user_id, community_id=community_id)
            .first()
        )

        if existing:
            return {"success": False, "message": "Kamu sudah bergabung."}

        membership = CommunityMember(
            user_id=user_id,
            community_id=community_id
        )

        db.add(membership)
        db.commit()

        return {"success": True, "message": "Berhasil bergabung ke komunitas."}

    except IntegrityError:
        db.rollback()
        return {"success": False, "message": "Keanggotaan sudah tersedia."}

    finally:
        db.close()


def get_user_communities(user_id):
    db = SessionLocal()

    try:
        memberships = (
            db.query(CommunityMember)
            .filter(CommunityMember.user_id == user_id)
            .all()
        )

        result = []

        for membership in memberships:
            community = (
                db.query(Community)
                .filter(Community.id == membership.community_id)
                .first()
            )

            if community:
                result.append({
                    "id": community.id,
                    "name": community.name,
                    "description": community.description
                })

        return result

    finally:
        db.close()
