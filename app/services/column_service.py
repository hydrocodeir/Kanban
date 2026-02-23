from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.column import Column
from app.models.board import Board
from app.models.project import Project
from app.services.cache import cache_invalidate_board


def create_column(db: Session, project_id: int, user_id: int, title: str) -> Column | None:
    project = db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.is_deleted == False)).scalar_one_or_none()
    if not project or not project.board:
        return None

    board: Board = project.board
    # position = last + 1
    last_pos = db.execute(
        select(Column.position)
        .where(Column.board_id == board.id, Column.is_deleted == False)
        .order_by(Column.position.desc())
        .limit(1)
    ).scalars().first()
    pos = (last_pos + 1) if last_pos is not None else 0

    col = Column(board_id=board.id, title=title, position=pos)
    db.add(col)
    db.commit()
    db.refresh(col)

    cache_invalidate_board(project_id)
    return col


def update_column(db: Session, column_id: int, title: str | None = None) -> Column | None:
    col = db.execute(select(Column).where(Column.id == column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        return None
    if title is not None and title.strip():
        col.title = title.strip()
    db.commit()
    db.refresh(col)
    return col


def soft_delete_column(db: Session, project_id: int, column_id: int) -> bool:
    col = db.execute(select(Column).where(Column.id == column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        return False
    col.is_deleted = True
    col.deleted_at = datetime.utcnow()
    db.commit()
    cache_invalidate_board(project_id)
    return True
