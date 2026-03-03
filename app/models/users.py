import typing
from datetime import datetime

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if typing.TYPE_CHECKING:
    from app.models import SolutionsOrm, UsersProgressesOrm


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(length=31), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=200), nullable=False)
    role: Mapped[str] = mapped_column(
        String(length=20), server_default=text("'student'"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )

    users_progresses: Mapped[list["UsersProgressesOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    solutions: Mapped[list["SolutionsOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
