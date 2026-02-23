from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.project import Project
from app.models.board import Board
from app.models.column import Column
from app.models.task import Task
from app.models.user import User
from app.services.cache import cache_get_board, cache_set_board


def get_board_data(db: Session, project_id: int, user_id: int) -> dict | None:
    cached = cache_get_board(project_id)
    if cached:
        return cached

    project = db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.is_deleted == False)).scalar_one_or_none()
    if not project or not project.board or project.board.is_deleted:
        return None

    board: Board = project.board
    cols = db.execute(select(Column).where(Column.board_id == board.id, Column.is_deleted == False).order_by(Column.position.asc(), Column.id.asc())).scalars().all()

    data_cols = []
    for col in cols:
        tasks_rows = db.execute(
            select(Task, User.full_name)
            .outerjoin(User, Task.assignee_id == User.id)
            .where(Task.column_id == col.id, Task.is_deleted == False)
            .order_by(Task.position.asc(), Task.id.asc())
        ).all()
        data_cols.append({
            "id": col.id,
            "title": col.title,
            "position": col.position,
            "tasks": [
                {
                    "id": t.id,
                    "assignee_id": t.assignee_id,
                    "assignee_name": assignee_name,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "status": t.status,
                    "position": t.position,
                }
                for (t, assignee_name) in tasks_rows
            ],
        })

    payload = {
        "project": {"id": project.id, "title": project.title, "description": project.description},
        "board": {"id": board.id, "title": board.title},
        "users": [
            {"id": u.id, "full_name": u.full_name}
            for u in db.execute(select(User).where(User.is_deleted == False, User.is_active == True).order_by(User.full_name.asc(), User.id.asc())).scalars().all()
        ],
        "current_user_id": user_id,
        "columns": data_cols,
    }

    cache_set_board(project_id, payload)
    return payload
