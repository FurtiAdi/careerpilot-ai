"""backfill legacy saved resumes

Revision ID: c34fdd9f62c4
Revises: 141f199ba79e
Create Date: 2026-09-30 11:35:54.292335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c34fdd9f62c4'
down_revision: Union[str, Sequence[str], None] = '141f199ba79e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO saved_resumes (
            user_id,
            storage_filename,
            original_filename,
            created_at
        )
        SELECT
            users.id,
            users.resume_filename,
            users.resume_filename,
            CURRENT_TIMESTAMP
        FROM users
        WHERE users.resume_filename IS NOT NULL
          AND users.resume_filename <> ''
          AND NOT EXISTS (
              SELECT 1
              FROM saved_resumes
              WHERE saved_resumes.user_id = users.id
                AND saved_resumes.storage_filename
                    = users.resume_filename
          )
        """
    )

    op.execute(
        """
        UPDATE tailored_resumes AS tailored_resume
        SET source_resume_id = saved_resume.id
        FROM saved_resumes AS saved_resume
        WHERE tailored_resume.source_resume_id IS NULL
          AND tailored_resume.user_id = saved_resume.user_id
          AND tailored_resume.source_resume_filename
              = saved_resume.storage_filename
        """
    )


def downgrade() -> None:
    # Keep backfilled data intact. The schema migration before this
    # revision owns table removal if the schema is rolled back.
    pass
