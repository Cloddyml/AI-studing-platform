import typing
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TaskTestsOrm, TopicsOrm


class TasksOrm(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    time_limit_sec: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("10")
    )
    memory_limit_mb: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("128")
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )

    topic: Mapped["TopicsOrm"] = relationship(back_populates="tasks")
    task_tests: Mapped[list["TaskTestsOrm"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
