from pydantic import BaseModel, Field
from app.schemas.common import ORMBase, SoftDeleteMixin


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None


class ProjectOut(ORMBase, SoftDeleteMixin):
    id: int
    user_id: int
    title: str
    description: str | None = None
