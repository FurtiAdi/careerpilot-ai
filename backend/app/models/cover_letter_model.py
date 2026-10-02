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


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'saved')",
            name="ck_cover_letters_status",
        ),
        CheckConstraint(
            "tone IN ('professional', 'warm', 'concise')",
            name="ck_cover_letters_tone",
        ),
        CheckConstraint(
            "length IN ('short', 'standard')",
            name="ck_cover_letters_length",
        ),
        UniqueConstraint(
            "user_id",
            "version_group_id",
            "version_number",
            name="uq_cover_letter_version",
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

    source_resume_id = Column(
        Integer,
        ForeignKey("saved_resumes.id"),
        nullable=False,
        index=True,
    )

    source_tailored_resume_id = Column(
        Integer,
        ForeignKey("tailored_resumes.id"),
        nullable=True,
        index=True,
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

    tone = Column(
        String(20),
        nullable=False,
        default="professional",
        server_default="professional",
    )

    length = Column(
        String(20),
        nullable=False,
        default="standard",
        server_default="standard",
    )

    content = Column(
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