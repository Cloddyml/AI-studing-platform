import typing

from sqlalchemy import Boolean, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TasksOrm


class TaskTestsOrm(Base):
    __tablename__ = "task_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    test_code: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    task: Mapped["TasksOrm"] = relationship(back_populates="task_tests")
