from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import ORMBase, SoftDeleteMixin


class TaskCreate(BaseModel):
    project_id: int
    column_id: int
    assignee_id: int | None = None
    title: str = Field(min_length=1, max_length=250)
    description: str | None = None
    priority: int = Field(default=2, ge=1, le=3)
    due_date: date | None = None


class TaskUpdate(BaseModel):
    assignee_id: int | None = None
    title: str | None = Field(default=None, max_length=250)
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=3)
    due_date: date | None = None
    status: str | None = None
    column_id: int | None = None
    position: int | None = None


class TaskOut(ORMBase, SoftDeleteMixin):
    id: int
    project_id: int
    column_id: int
    assignee_id: int | None = None
    assignee_name: str | None = None
    title: str
    description: str | None = None
    priority: int
    due_date: date | None = None
    status: str
    position: int
