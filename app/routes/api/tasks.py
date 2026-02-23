from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.routes.api.deps import get_db
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.models.task import Task
from app.models.column import Column
from app.services.cache import cache_invalidate_board

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db)):
    tasks = db.execute(select(Task).where(Task.project_id == project_id, Task.is_deleted == False).order_by(Task.created_at.desc())).scalars().all()
    return list(tasks)


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    col = db.execute(select(Column).where(Column.id == payload.column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    last_pos = db.execute(
        select(Task.position)
        .where(Task.column_id == payload.column_id, Task.is_deleted == False)
        .order_by(Task.position.desc())
        .limit(1)
    ).scalars().first()
    pos = (last_pos + 1) if last_pos is not None else 0
    task = Task(
        project_id=payload.project_id,
        column_id=payload.column_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        status=col.title,
        position=pos,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    cache_invalidate_board(task.project_id)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, val)

    db.commit()
    db.refresh(task)
    cache_invalidate_board(task.project_id)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_deleted = True
    task.deleted_at = datetime.utcnow()
    db.commit()
    cache_invalidate_board(task.project_id)
    return {"ok": True}
