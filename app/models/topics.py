import typing
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TasksOrm, UsersProgressesOrm


class TopicsOrm(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(length=100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )

    tasks: Mapped[list["TasksOrm"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    users_progresses: Mapped[list["UsersProgressesOrm"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
