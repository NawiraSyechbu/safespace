
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint
)

from backend.database.connection import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    community_id = Column(
        Integer,
        ForeignKey("communities.id"),
        nullable=False
    )

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    moderation_status = Column(
        String(30),
        nullable=False,
        default="pending_review",
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "moderation_status IN "
            "('approved', 'blocked', 'pending_review')",
            name="check_post_moderation_status"
        ),
    )
