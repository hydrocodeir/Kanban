from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# نسخه مینیمال: کاربر ثابت (بدون احراز هویت)
DEFAULT_USER_ID = 1
