import typing
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import TopicsOrm, UsersOrm


class UsersProgressesOrm(Base):
    __tablename__ = "users_progresses"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    tasks_total: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    tasks_solved: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    user: Mapped["UsersOrm"] = relationship(back_populates="users_progresses")
    topic: Mapped["TopicsOrm"] = relationship(back_populates="users_progresses")
