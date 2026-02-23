from sqlalchemy.orm import Session

from app.models.entities import ActivityLog


def log_action(db: Session, user_id: int, action: str, target_type: str, target_id: int) -> None:
    db.add(ActivityLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id))
    db.commit()
