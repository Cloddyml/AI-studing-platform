"""submissions: add updated_at, submission_status enum, updated_at trigger

Revision ID: bc6cdf697551
Revises: 5bad42829a42
Create Date: 2026-03-14 01:01:47.025535

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc6cdf697551"
down_revision: Union[str, Sequence[str], None] = "5bad42829a42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём тип enum в PostgreSQL
    submission_status = sa.Enum(
        "pending",
        "running",
        "accepted",
        "wrong_answer",
        "time_limit",
        "memory_limit",
        "runtime_error",
        "internal_error",
        name="submission_status",
    )
    submission_status.create(op.get_bind(), checkfirst=True)

    # 2. ВАЖНО: сначала убираем server_default — PostgreSQL не умеет
    #    автоматически привести строковый дефолт к enum при ALTER TYPE
    op.alter_column("submissions", "status", server_default=None)

    # 3. Меняем тип колонки string → enum через явный CAST
    op.alter_column(
        "submissions",
        "status",
        existing_type=sa.String(length=20),
        type_=submission_status,
        postgresql_using="status::submission_status",
        nullable=False,
    )

    # 4. Возвращаем server_default уже с правильным приведением типа
    op.alter_column(
        "submissions",
        "status",
        server_default=sa.text("'pending'::submission_status"),
    )

    # 5. Добавляем timezone к существующей created_at
    # (если в БД она была без timezone)
    op.alter_column(
        "submissions",
        "created_at",
        existing_type=sa.DateTime(timezone=False),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    # 6. Добавляем updated_at с timezone
    op.add_column(
        "submissions",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # 7. Триггер для автоматического обновления updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_submissions_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_submissions_updated_at
        BEFORE UPDATE ON submissions
        FOR EACH ROW
        EXECUTE FUNCTION update_submissions_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_submissions_updated_at ON submissions;")
    op.execute("DROP FUNCTION IF EXISTS update_submissions_updated_at();")

    op.drop_column("submissions", "updated_at")

    # При откате: убираем enum-дефолт перед сменой типа (та же проблема в обратную сторону)
    op.alter_column("submissions", "status", server_default=None)

    op.alter_column(
        "submissions",
        "status",
        existing_type=sa.Enum(name="submission_status"),
        type_=sa.String(length=20),
        postgresql_using="status::text",
        nullable=False,
    )

    op.alter_column(
        "submissions",
        "status",
        server_default=sa.text("'pending'"),
    )

    op.alter_column(
        "submissions",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(timezone=False),
    )

    sa.Enum(name="submission_status").drop(op.get_bind(), checkfirst=True)
