from pydantic import BaseModel, Field
from app.schemas.common import ORMBase, SoftDeleteMixin


class ColumnCreate(BaseModel):
    board_id: int
    title: str = Field(min_length=1, max_length=200)
    position: int = 0


class ColumnUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    position: int | None = None


class ColumnOut(ORMBase, SoftDeleteMixin):
    id: int
    board_id: int
    title: str
    position: int
