
from backend.database.connection import SessionLocal
from backend.models.moderation_action import ModerationAction
from backend.models.prediction import AIPrediction


def get_moderation_history(content_type, content_id):
    db = SessionLocal()

    try:
        actions = (
            db.query(ModerationAction)
            .filter(
                ModerationAction.content_type == content_type,
                ModerationAction.content_id == content_id
            )
            .order_by(ModerationAction.created_at.asc())
            .all()
        )

        predictions = (
            db.query(AIPrediction)
            .filter(
                AIPrediction.content_type == content_type,
                AIPrediction.content_id == content_id
            )
            .order_by(AIPrediction.created_at.asc())
            .all()
        )

        return {
            "actions": [
                {
                    "action": item.action,
                    "moderator_id": item.moderator_id,
                    "notes": item.notes,
                    "created_at": item.created_at
                }
                for item in actions
            ],
            "predictions": [
                {
                    "task_name": item.task_name,
                    "predicted_labels": item.predicted_labels,
                    "probabilities": item.probabilities,
                    "created_at": item.created_at
                }
                for item in predictions
            ]
        }

    finally:
        db.close()
