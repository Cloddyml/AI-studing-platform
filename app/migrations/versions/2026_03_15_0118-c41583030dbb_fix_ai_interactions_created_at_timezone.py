"""fix_ai_interactions_created_at_timezone

Revision ID: c41583030dbb
Revises: bc6cdf697551
Create Date: 2026-03-15 01:18:33.796317

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c41583030dbb"
down_revision: Union[str, Sequence[str], None] = "bc6cdf697551"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "solutions",
        "is_tests_passed",
        server_default=sa.text("true"),
    )
    op.create_check_constraint(
        "ck_solutions_tests_passed",
        "solutions",
        "is_tests_passed = true",
    )


def downgrade() -> None:
    op.drop_constraint("ck_solutions_tests_passed", "solutions")
    op.alter_column(
        "solutions",
        "is_tests_passed",
        server_default=sa.text("false"),
    )
