from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)

from app.database.database import Base


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'saved')",
            name="ck_tailored_resumes_status",
        ),
        UniqueConstraint(
            "user_id",
            "version_group_id",
            "version_number",
            name="uq_tailored_resume_version",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    source_analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=False,
        index=True,
    )

    source_resume_filename = Column(
        String,
        nullable=False,
    )

    version_group_id = Column(
        String(36),
        nullable=False,
        index=True,
    )

    version_number = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    status = Column(
        String(20),
        nullable=False,
        default="draft",
        server_default="draft",
    )

    content = Column(
        JSON,
        nullable=False,
    )

    match_snapshot = Column(
        JSON,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )