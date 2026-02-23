from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    admin = 'admin'
    user = 'user'


class TaskStatus(str, Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.user, nullable=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Board(Base):
    __tablename__ = 'boards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)

    owner = relationship('User')


class Column(Base):
    __tablename__ = 'columns'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), index=True)

    board = relationship('Board')


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default='')
    priority: Mapped[str] = mapped_column(String(50), default='medium')
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus), default=TaskStatus.todo, nullable=False)
    column_id: Mapped[int] = mapped_column(ForeignKey('columns.id', ondelete='CASCADE'), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    column = relationship('Column')


class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


Index('ix_activity_logs_created_at', ActivityLog.created_at)
