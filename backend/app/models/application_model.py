from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database.database import Base


APPLICATION_STATUSES = (
    "saved",
    "applied",
    "screening",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
)


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        CheckConstraint(
            "status IN ("
            "'saved', 'applied', 'screening', 'interview', "
            "'offer', 'rejected', 'withdrawn'"
            ")",
            name="ck_applications_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="saved",
        server_default="saved",
        index=True,
    )

    job_url = Column(String(2048), nullable=True)
    job_description = Column(Text, nullable=True)

    applied_at = Column(Date, nullable=True)
    next_action_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=True,
        index=True,
    )

    tailored_resume_id = Column(
        Integer,
        ForeignKey("tailored_resumes.id"),
        nullable=True,
        index=True,
    )

    cover_letter_id = Column(
        Integer,
        ForeignKey("cover_letters.id"),
        nullable=True,
        index=True,
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


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    __table_args__ = (
        CheckConstraint(
            "event_type = 'status_changed'",
            name="ck_application_events_type",
        ),
        CheckConstraint(
            "new_status IN ("
            "'saved', 'applied', 'screening', 'interview', "
            "'offer', 'rejected', 'withdrawn'"
            ")",
            name="ck_application_events_new_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    event_type = Column(
        String(30),
        nullable=False,
        default="status_changed",
        server_default="status_changed",
    )

    previous_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)

    note = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )