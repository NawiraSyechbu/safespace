
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from backend.database.connection import Base


class ModerationAction(Base):
    __tablename__ = "moderation_actions"

    id = Column(Integer, primary_key=True, index=True)

    moderator_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    content_type = Column(
        String(20),
        nullable=False
    )

    content_id = Column(
        Integer,
        nullable=False
    )

    action = Column(
        String(30),
        nullable=False
    )

    notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
