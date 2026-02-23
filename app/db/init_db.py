from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models import _all  # noqa: F401
from app.models.user import User
from app.models.project import Project
from app.models.board import Board
from app.models.column import Column
from app.core.security import hash_password

DEFAULT_COLUMNS = ["در انتظار انجام", "در حال انجام", "انجام شده"]


def create_all():
    Base.metadata.create_all(bind=engine)


def _column_exists(db: Session, table: str, column: str) -> bool:
    q = text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
    )
    return (db.execute(q, {"t": table, "c": column}).scalar() or 0) > 0


def ensure_runtime_migrations(db: Session):
    """مهاجرت سبک برای محیط‌های بدون Alembic (مثل همین پروژه).

    اگر ستون‌های جدید وجود نداشته باشند، آن‌ها را اضافه می‌کند تا نسخه‌های قبلی DB هم کار کنند.
    """
    # users.password_hash
    if not _column_exists(db, "users", "password_hash"):
        db.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL"))
        db.commit()

    # tasks.assignee_id
    if not _column_exists(db, "tasks", "assignee_id"):
        db.execute(text("ALTER TABLE tasks ADD COLUMN assignee_id BIGINT NULL"))
        # ایندکس
        try:
            db.execute(text("CREATE INDEX idx_tasks_assignee_id ON tasks (assignee_id)"))
        except Exception:
            pass
        db.commit()



def seed_default_user_and_sample(db: Session):
    user = db.execute(
        select(User)
        .where(User.email == "demo@example.com")
        .order_by(User.id.asc())
        .limit(1)
    ).scalars().first()
    if not user:
        user = User(full_name="کاربر نمونه", email="demo@example.com", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    # تنظیم رمز عبور برای کاربر نمونه (در صورت نبود)
    if not getattr(user, 'password_hash', None):
        user.password_hash = hash_password('admin123')
        db.commit()

    # create one sample project if none
    project = db.execute(
        select(Project)
        .where(Project.user_id == user.id, Project.is_deleted == False)
        .order_by(Project.id.asc())
        .limit(1)
    ).scalars().first()
    if not project:
        project = Project(user_id=user.id, title="پروژه نمونه", description="این یک پروژه نمونه است.")
        db.add(project)
        db.commit()
        db.refresh(project)

        board = Board(project_id=project.id, title="برد کانبان")
        db.add(board)
        db.commit()
        db.refresh(board)

        for i, title in enumerate(DEFAULT_COLUMNS):
            db.add(Column(board_id=board.id, title=title, position=i))
        db.commit()


def main():
    create_all()
    db = SessionLocal()
    try:
        seed_default_user_and_sample(db)
    finally:
        db.close()
    print("DB initialized.")


if __name__ == "__main__":
    main()
