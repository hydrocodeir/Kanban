from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.entities import User, UserRole
from app.schemas.api import UserOut, UserUpdate
from app.services.activity import log_action

router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('/', response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User)).all()


@router.get('/me', response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch('/{user_id}', response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='کاربر یافت نشد')
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='غیرمجاز')

    data = payload.model_dump(exclude_none=True)
    if 'role' in data and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail='فقط مدیر می‌تواند نقش را تغییر دهد')

    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    log_action(db, current_user.id, 'update_user', 'user', user.id)
    return user
