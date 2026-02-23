from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, ForeignKey, Integer
from app.db.base import Base
from app.models.base import TimestampSoftDeleteMixin


class Column(Base, TimestampSoftDeleteMixin):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("boards.id"), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column")
