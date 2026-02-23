from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, BigInteger, ForeignKey, Integer, Date
from app.db.base import Base
from app.models.base import TimestampSoftDeleteMixin


class Task(Base, TimestampSoftDeleteMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), index=True, nullable=False)
    column_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("columns.id"), index=True, nullable=False)

    assignee_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), index=True, nullable=True)

    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    priority: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1..3
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    project = relationship("Project", back_populates="tasks")
    column = relationship("Column", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])

    @property
    def assignee_name(self):
        return self.assignee.full_name if getattr(self, 'assignee', None) else None
