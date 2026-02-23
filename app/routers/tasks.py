from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import ensure_owner_or_admin, get_current_user
from app.models.entities import Board, Column, Task, TaskStatus, User
from app.schemas.api import TaskIn, TaskOut, TaskUpdate
from app.services.activity import log_action
from app.services.telegram import notify_user

router = APIRouter(prefix='/api/tasks', tags=['tasks'])


def _board_from_column(db: Session, column_id: int) -> Board:
    column = db.get(Column, column_id)
    if not column:
        raise HTTPException(status_code=404, detail='ستون یافت نشد')
    board = db.get(Board, column.board_id)
    if not board:
        raise HTTPException(status_code=404, detail='بورد یافت نشد')
    return board


@router.get('/column/{column_id}', response_model=list[TaskOut])
def list_tasks(column_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = _board_from_column(db, column_id)
    ensure_owner_or_admin(board.owner_id, current_user)
    return db.scalars(select(Task).where(Task.column_id == column_id)).all()


@router.post('/', response_model=TaskOut)
async def create_task(payload: TaskIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = _board_from_column(db, payload.column_id)
    ensure_owner_or_admin(board.owner_id, current_user)
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    log_action(db, current_user.id, 'create_task', 'task', task.id)
    if task.assignee_id:
        await notify_user(db, task.assignee_id, 'یک وظیفه جدید به شما اختصاص داده شد')
    return task


@router.patch('/{task_id}', response_model=TaskOut)
async def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='وظیفه یافت نشد')
    board = _board_from_column(db, task.column_id)
    ensure_owner_or_admin(board.owner_id, current_user)

    before_status = task.status
    for key, value in payload.model_dump(exclude_none=True).items():
        if key == 'status':
            value = TaskStatus(value)
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    log_action(db, current_user.id, 'update_task', 'task', task.id)
    if before_status != task.status and task.assignee_id:
        log_action(db, current_user.id, 'status_change', 'task', task.id)
        await notify_user(db, task.assignee_id, 'وضعیت یک وظیفه تغییر کرد')
    return task


@router.delete('/{task_id}', status_code=204)
async def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='وظیفه یافت نشد')
    board = _board_from_column(db, task.column_id)
    ensure_owner_or_admin(board.owner_id, current_user)
    assignee_id = task.assignee_id
    db.delete(task)
    db.commit()
    log_action(db, current_user.id, 'delete_task', 'task', task_id)
    if assignee_id:
        await notify_user(db, assignee_id, 'یک وظیفه حذف شد')
