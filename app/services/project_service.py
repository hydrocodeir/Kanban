from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from app.models.project import Project
from app.models.board import Board
from app.models.column import Column
from app.models.task import Task
from app.services.cache import cache_invalidate_board

DEFAULT_COLUMNS = ["در انتظار انجام", "در حال انجام", "انجام شده"]


def list_projects(db: Session, user_id: int) -> list[Project]:
    stmt = select(Project).where(Project.user_id == user_id, Project.is_deleted == False).order_by(Project.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_project(db: Session, project_id: int, user_id: int) -> Project | None:
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == user_id,
        Project.is_deleted == False,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_project(db: Session, user_id: int, title: str, description: str | None) -> Project:
    project = Project(user_id=user_id, title=title, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)

    board = Board(project_id=project.id, title="برد کانبان")
    db.add(board)
    db.commit()
    db.refresh(board)

    for i, col_title in enumerate(DEFAULT_COLUMNS):
        db.add(Column(board_id=board.id, title=col_title, position=i))
    db.commit()

    return project



def soft_delete_project(db: Session, project_id: int, user_id: int) -> bool:
    project = get_project(db, project_id, user_id)
    if not project:
        return False

    now = datetime.utcnow()

    # project
    project.is_deleted = True
    project.deleted_at = now

    # board
    if project.board:
        project.board.is_deleted = True
        project.board.deleted_at = now

        # columns
        cols = db.execute(
            select(Column).where(Column.board_id == project.board.id, Column.is_deleted == False)
        ).scalars().all()
        for col in cols:
            col.is_deleted = True
            col.deleted_at = now

    # tasks (safe even if columns missing)
    tasks = db.execute(
        select(Task).where(Task.project_id == project.id, Task.is_deleted == False)
    ).scalars().all()
    for t in tasks:
        t.is_deleted = True
        t.deleted_at = now

    db.commit()
    cache_invalidate_board(project.id)
    return True
