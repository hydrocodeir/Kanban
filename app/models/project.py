from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, BigInteger, ForeignKey
from app.db.base import Base
from app.models.base import TimestampSoftDeleteMixin


class Project(Base, TimestampSoftDeleteMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="projects")
    board = relationship("Board", back_populates="project", uselist=False)
    tasks = relationship("Task", back_populates="project")
