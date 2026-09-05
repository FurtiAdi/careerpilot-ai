"""add tailored resumes

Revision ID: caca6cb7c085
Revises: 8b876267a8eb
Create Date: 2026-09-05 00:49:57.538730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caca6cb7c085'
down_revision: Union[str, Sequence[str], None] = '8b876267a8eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tailored_resumes",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "source_analysis_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "source_resume_filename",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "version_group_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "match_snapshot",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'saved')",
            name="ck_tailored_resumes_status",
        ),
        sa.ForeignKeyConstraint(
            ["source_analysis_id"],
            ["analyses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "version_group_id",
            "version_number",
            name="uq_tailored_resume_version",
        ),
    )

    op.create_index(
        op.f("ix_tailored_resumes_id"),
        "tailored_resumes",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tailored_resumes_source_analysis_id"),
        "tailored_resumes",
        ["source_analysis_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tailored_resumes_user_id"),
        "tailored_resumes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tailored_resumes_version_group_id"),
        "tailored_resumes",
        ["version_group_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_tailored_resumes_version_group_id"),
        table_name="tailored_resumes",
    )
    op.drop_index(
        op.f("ix_tailored_resumes_user_id"),
        table_name="tailored_resumes",
    )
    op.drop_index(
        op.f("ix_tailored_resumes_source_analysis_id"),
        table_name="tailored_resumes",
    )
    op.drop_index(
        op.f("ix_tailored_resumes_id"),
        table_name="tailored_resumes",
    )
    op.drop_table("tailored_resumes")
