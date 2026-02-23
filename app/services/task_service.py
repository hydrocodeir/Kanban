from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.task import Task
from app.models.column import Column
from app.models.project import Project
from app.services.cache import cache_invalidate_board


def create_task(
    db: Session,
    project_id: int,
    user_id: int,
    column_id: int,
    assignee_id: int | None,
    title: str,
    description: str | None,
    priority: int,
    due_date,
) -> Task | None:
    # validate project ownership
    project = db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.is_deleted == False)).scalar_one_or_none()
    if not project:
        return None

    col = db.execute(select(Column).where(Column.id == column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        return None

    # compute position
    last_pos = db.execute(
        select(Task.position)
        .where(Task.column_id == column_id, Task.is_deleted == False)
        .order_by(Task.position.desc())
        .limit(1)
    ).scalars().first()
    pos = (last_pos + 1) if last_pos is not None else 0

    task = Task(
        project_id=project_id,
        column_id=column_id,
        assignee_id=assignee_id,
        title=title.strip(),
        description=description.strip() if description else None,
        priority=priority,
        due_date=due_date,
        status=col.title,
        position=pos,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    cache_invalidate_board(project_id)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False)).scalar_one_or_none()


def soft_delete_task(db: Session, task_id: int) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None
    task.is_deleted = True
    task.deleted_at = datetime.utcnow()
    db.commit()
    cache_invalidate_board(task.project_id)
    return task


def move_task(db: Session, task_id: int, to_column_id: int, order_ids: list[int]) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None

    col = db.execute(select(Column).where(Column.id == to_column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        return None

    task.column_id = to_column_id
    task.status = col.title
    db.commit()

    # reorder tasks in target column based on provided order
    # order_ids contains task IDs in desired order for that column
    for pos, tid in enumerate(order_ids):
        t = db.execute(select(Task).where(Task.id == tid, Task.is_deleted == False)).scalar_one_or_none()
        if t and t.column_id == to_column_id:
            t.position = pos
    db.commit()

    cache_invalidate_board(task.project_id)
    db.refresh(task)
    return task



def update_task(
    db: Session,
    task_id: int,
    assignee_id: int | None,
    title: str,
    description: str | None,
    priority: int,
    due_date,
) -> Task | None:
    task = get_task(db, task_id=task_id)
    if not task:
        return None

    task.title = title.strip()
    task.assignee_id = assignee_id
    task.description = description.strip() if description else None
    task.priority = int(priority)
    task.due_date = due_date
    db.commit()
    db.refresh(task)
    cache_invalidate_board(task.project_id)
    return task

