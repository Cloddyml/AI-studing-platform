import typing
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TasksOrm, UsersOrm


class SolutionsOrm(Base):
    __tablename__ = "solutions"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_user_task_solution"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    is_tests_passed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    solved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    user: Mapped["UsersOrm"] = relationship(back_populates="solutions")
    task: Mapped["TasksOrm"] = relationship(back_populates="solutions")
