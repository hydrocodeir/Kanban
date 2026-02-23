from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password, verify_password


def get_user(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id, User.is_deleted == False, User.is_active == True)).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email, User.is_deleted == False)).scalar_one_or_none()


def list_users(db: Session) -> list[User]:
    return db.execute(select(User).where(User.is_deleted == False, User.is_active == True).order_by(User.full_name.asc(), User.id.asc())).scalars().all()


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email=email.strip().lower())
    if not user:
        return None
    if not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.is_deleted or not user.is_active:
        return None
    return user


def create_user(db: Session, full_name: str, email: str, password: str) -> User:
    user = User(
        full_name=full_name.strip(),
        email=email.strip().lower(),
        password_hash=hash_password(password),
        is_active=True,
        is_deleted=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
