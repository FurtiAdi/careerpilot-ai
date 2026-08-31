"""baseline schema

Revision ID: 8b876267a8eb
Revises: 
Create Date: 2026-08-22 21:51:00.015852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b876267a8eb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "profile_picture_filename",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "resume_filename",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False,
    )

    op.create_table(
        "analyses",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "job_description",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "candidate_skills",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "match_score",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "ai_summary",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_analyses_id"),
        "analyses",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_analyses_id"),
        table_name="analyses",
    )

    op.drop_table("analyses")

    op.drop_index(
        op.f("ix_users_id"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    op.drop_table("users")
