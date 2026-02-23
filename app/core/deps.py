from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.entities import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
_login_attempts = defaultdict(list)


def check_login_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else 'unknown'
    now = datetime.utcnow()
    window = timedelta(seconds=settings.rate_limit_window_seconds)
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < window]
    if len(_login_attempts[ip]) >= settings.max_login_attempts_per_window:
        raise HTTPException(status_code=429, detail='تعداد تلاش‌های ورود بیش از حد مجاز است')
    _login_attempts[ip].append(now)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='احراز هویت نامعتبر است')
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='کاربر یافت نشد')
    return user


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=401, detail='ورود لازم است')
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail='توکن نامعتبر است')
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail='کاربر نامعتبر است')
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail='دسترسی مدیر لازم است')
    return current_user


def require_admin_cookie(current_user: User = Depends(get_current_user_from_cookie)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail='دسترسی مدیر لازم است')
    return current_user


def ensure_owner_or_admin(owner_id: int, current_user: User) -> None:
    if current_user.role != UserRole.admin and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='دسترسی غیرمجاز')


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))
