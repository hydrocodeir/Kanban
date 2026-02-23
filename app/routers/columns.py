from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import ensure_owner_or_admin, get_current_user
from app.models.entities import Board, Column, User
from app.schemas.api import ColumnIn, ColumnOut
from app.services.activity import log_action

router = APIRouter(prefix='/api/columns', tags=['columns'])


@router.get('/{board_id}', response_model=list[ColumnOut])
def list_columns(board_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='بورد یافت نشد')
    ensure_owner_or_admin(board.owner_id, current_user)
    return db.scalars(select(Column).where(Column.board_id == board_id)).all()


@router.post('/', response_model=ColumnOut)
def create_column(payload: ColumnIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.get(Board, payload.board_id)
    if not board:
        raise HTTPException(status_code=404, detail='بورد یافت نشد')
    ensure_owner_or_admin(board.owner_id, current_user)
    col = Column(**payload.model_dump())
    db.add(col)
    db.commit()
    db.refresh(col)
    log_action(db, current_user.id, 'create_column', 'column', col.id)
    return col
