from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Literal['admin', 'user']
    telegram_chat_id: str | None
    notify_enabled: bool
    dark_mode: bool


class UserUpdate(BaseModel):
    role: Literal['admin', 'user'] | None = None
    telegram_chat_id: str | None = None
    notify_enabled: bool | None = None
    dark_mode: bool | None = None


class BoardIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)


class BoardOut(BoardIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int


class ColumnIn(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    board_id: int


class ColumnOut(ColumnIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TaskIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = ''
    priority: str = 'medium'
    status: Literal['todo', 'in_progress', 'done'] = 'todo'
    column_id: int
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: Literal['todo', 'in_progress', 'done'] | None = None
    column_id: int | None = None
    assignee_id: int | None = None


class TaskOut(TaskIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    action: str
    target_type: str
    target_id: int
    created_at: datetime
