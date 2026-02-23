from datetime import datetime
from pydantic import BaseModel


class ORMBase(BaseModel):
    # Pydantic v2: allow loading from ORM objects
    model_config = {"from_attributes": True}


class SoftDeleteMixin(BaseModel):
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
