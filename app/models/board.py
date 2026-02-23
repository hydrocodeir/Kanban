from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, ForeignKey
from app.db.base import Base
from app.models.base import TimestampSoftDeleteMixin


class Board(Base, TimestampSoftDeleteMixin):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), unique=True, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    project = relationship("Project", back_populates="board")
    columns = relationship("Column", back_populates="board")
