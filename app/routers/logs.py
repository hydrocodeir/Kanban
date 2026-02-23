from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.entities import ActivityLog, User, UserRole
from app.schemas.api import ActivityOut

router = APIRouter(prefix='/api/logs', tags=['activity'])


@router.get('/', response_model=list[ActivityOut])
def list_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    if current_user.role != UserRole.admin:
        query = query.where(ActivityLog.user_id == current_user.id)
    return db.scalars(query).all()
