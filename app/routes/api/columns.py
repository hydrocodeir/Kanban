from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.routes.api.deps import get_db
from app.schemas.column import ColumnCreate, ColumnOut, ColumnUpdate
from app.models.column import Column
from app.services.column_service import update_column
from app.services.cache import cache_invalidate_board
from app.models.board import Board

router = APIRouter(prefix="/columns", tags=["columns"])


@router.get("", response_model=list[ColumnOut])
def list_columns(board_id: int, db: Session = Depends(get_db)):
    cols = db.execute(select(Column).where(Column.board_id == board_id, Column.is_deleted == False).order_by(Column.position.asc())).scalars().all()
    return list(cols)


@router.post("", response_model=ColumnOut, status_code=201)
def create_column(payload: ColumnCreate, db: Session = Depends(get_db)):
    # basic: just create for provided board_id
    board = db.execute(select(Board).where(Board.id == payload.board_id, Board.is_deleted == False)).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    col = Column(board_id=payload.board_id, title=payload.title, position=payload.position)
    db.add(col)
    db.commit()
    db.refresh(col)
    cache_invalidate_board(board.project_id)
    return col


@router.put("/{column_id}", response_model=ColumnOut)
def update_column_api(column_id: int, payload: ColumnUpdate, db: Session = Depends(get_db)):
    col = update_column(db, column_id=column_id, title=payload.title)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    # best-effort invalidation (need project_id)
    board = db.execute(select(Board).where(Board.id == col.board_id)).scalar_one_or_none()
    if board:
        cache_invalidate_board(board.project_id)
    return col


@router.delete("/{column_id}")
def delete_column_api(column_id: int, db: Session = Depends(get_db)):
    col = db.execute(select(Column).where(Column.id == column_id, Column.is_deleted == False)).scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    col.is_deleted = True
    col.deleted_at = datetime.utcnow()
    db.commit()
    board = db.execute(select(Board).where(Board.id == col.board_id)).scalar_one_or_none()
    if board:
        cache_invalidate_board(board.project_id)
    return {"ok": True}
