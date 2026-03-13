"""fix_datetime_timezone_and_trigger

Revision ID: 5bad42829a42
Revises: f02588e15c73
Create Date: 2026-03-14 00:39:11.492986

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5bad42829a42"
down_revision: Union[str, Sequence[str], None] = "f02588e15c73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )

    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
    """)

    op.alter_column(
        "topics",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "solutions",
        "solved_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="solved_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "submissions",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users_progresses",
        "completed_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="completed_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "ai_interactions",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    op.alter_column(
        "ai_interactions",
        "response_time",
        new_column_name="response_time_ms",
        existing_type=sa.Integer(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "ai_interactions",
        "response_time_ms",
        new_column_name="response_time",
        existing_type=sa.Integer(),
        existing_nullable=True,
    )

    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at;")

    for table, column in [
        ("users", "created_at"),
        ("users", "updated_at"),
        ("topics", "created_at"),
        ("tasks", "created_at"),
        ("solutions", "solved_at"),
        ("submissions", "created_at"),
        ("ai_interactions", "created_at"),
    ]:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )

    op.alter_column(
        "users_progresses",
        "completed_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="completed_at AT TIME ZONE 'UTC'",
    )
