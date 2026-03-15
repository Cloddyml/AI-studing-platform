"""fixes

Revision ID: 6989b05d867e
Revises: c41583030dbb
Create Date: 2026-03-15 03:06:18.458657

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6989b05d867e"
down_revision: Union[str, Sequence[str], None] = "c41583030dbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Гарантируем, что в solutions.is_tests_passed хранится только True.
    #    solutions — таблица финальных принятых решений,
    #    is_tests_passed здесь всегда True по архитектуре.
    op.execute("""
        ALTER TABLE solutions
        ADD CONSTRAINT chk_solutions_tests_passed
        CHECK (is_tests_passed = true);
    """)

    # 2. Индекс для быстрого поиска submissions по пользователю (поллинг + статистика)
    op.create_index(
        "ix_submissions_user_id",
        "submissions",
        ["user_id"],
    )

    # 3. Индекс для быстрого поиска solutions по пользователю (статистика + прогресс)
    op.create_index(
        "ix_solutions_user_id",
        "solutions",
        ["user_id"],
    )

    # 4. Индекс для users_progresses по user_id (запрос прогресса)
    op.create_index(
        "ix_users_progresses_user_id",
        "users_progresses",
        ["user_id"],
    )

    # 5. Индекс для ai_interactions по user_id (история взаимодействий)
    op.create_index(
        "ix_ai_interactions_user_id",
        "ai_interactions",
        ["user_id"],
    )


def downgrade() -> None:
    op.execute("""
        ALTER TABLE solutions
        DROP CONSTRAINT IF EXISTS chk_solutions_tests_passed;
    """)
    op.drop_index("ix_submissions_user_id", "submissions")
    op.drop_index("ix_solutions_user_id", "solutions")
    op.drop_index("ix_users_progresses_user_id", "users_progresses")
    op.drop_index("ix_ai_interactions_user_id", "ai_interactions")
