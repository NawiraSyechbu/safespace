
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON
)

from backend.database.connection import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)

    content_type = Column(
        String(20),
        nullable=False
    )

    content_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    task_name = Column(
        String(50),
        nullable=False
    )

    predicted_labels = Column(JSON, nullable=True)

    probabilities = Column(JSON, nullable=True)

    confidence = Column(
        String(30),
        nullable=True
    )

    model_version = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
