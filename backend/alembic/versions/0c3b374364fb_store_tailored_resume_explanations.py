"""store tailored resume explanations

Revision ID: 0c3b374364fb
Revises: caca6cb7c085
Create Date: 2026-09-05 22:41:11.342674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c3b374364fb'
down_revision: Union[str, Sequence[str], None] = 'caca6cb7c085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tailored_resumes",
        sa.Column(
            "emphasized_items",
            sa.JSON(),
            server_default="[]",
            nullable=False,
        ),
    )
    op.add_column(
        "tailored_resumes",
        sa.Column(
            "reordered_items",
            sa.JSON(),
            server_default="[]",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "tailored_resumes",
        "reordered_items",
    )
    op.drop_column(
        "tailored_resumes",
        "emphasized_items",
    )
