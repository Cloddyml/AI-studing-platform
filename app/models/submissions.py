import enum
import typing
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy import (
    Enum as PgEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TasksOrm, UsersOrm


class SubmissionStatus(str, enum.Enum):
    """Статусы жизненного цикла попытки выполнения кода."""

    PENDING = "pending"  # В очереди Celery
    RUNNING = "running"  # Выполняется в sandbox
    ACCEPTED = "accepted"  # Все тесты пройдены
    WRONG_ANSWER = "wrong_answer"  # Неверный ответ
    TIME_LIMIT = "time_limit"  # Превышен лимит времени
    MEMORY_LIMIT = "memory_limit"  # Превышен лимит памяти
    RUNTIME_ERROR = "runtime_error"  # Ошибка во время выполнения
    INTERNAL_ERROR = "internal_error"  # Ошибка на стороне сервера


class SubmissionsOrm(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        PgEnum(SubmissionStatus, name="submission_status", create_type=True),
        nullable=False,
        server_default=text("'pending'"),
    )
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_tests_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        server_onupdate=FetchedValue(),
    )

    user: Mapped["UsersOrm"] = relationship(back_populates="submissions")
    task: Mapped["TasksOrm"] = relationship(back_populates="submissions")
