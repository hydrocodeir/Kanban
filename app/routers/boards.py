from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import ensure_owner_or_admin, get_current_user
from app.models.entities import Board, Column, User, UserRole
from app.schemas.api import BoardIn, BoardOut
from app.services.activity import log_action
from app.services.telegram import notify_user

router = APIRouter(prefix='/api/boards', tags=['boards'])


@router.get('/', response_model=list[BoardOut])
def list_boards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Board)
    if current_user.role != UserRole.admin:
        q = q.where(Board.owner_id == current_user.id)
    return db.scalars(q).all()


@router.post('/', response_model=BoardOut)
async def create_board(payload: BoardIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = Board(title=payload.title, owner_id=current_user.id)
    db.add(board)
    db.commit()
    db.refresh(board)
    for title in ['برای انجام', 'در حال انجام', 'انجام‌شده']:
        db.add(Column(title=title, board_id=board.id))
    db.commit()
    log_action(db, current_user.id, 'create_board', 'board', board.id)
    await notify_user(db, current_user.id, 'یک بورد جدید ایجاد شد')
    return board


@router.put('/{board_id}', response_model=BoardOut)
def update_board(board_id: int, payload: BoardIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='بورد یافت نشد')
    ensure_owner_or_admin(board.owner_id, current_user)
    board.title = payload.title
    db.commit()
    db.refresh(board)
    log_action(db, current_user.id, 'update_board', 'board', board.id)
    return board


@router.delete('/{board_id}', status_code=204)
def delete_board(board_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='بورد یافت نشد')
    ensure_owner_or_admin(board.owner_id, current_user)
    db.delete(board)
    db.commit()
    log_action(db, current_user.id, 'delete_board', 'board', board_id)
