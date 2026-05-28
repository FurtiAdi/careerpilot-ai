from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime, 
    ForeignKey
)

from datetime import datetime

from app.database.database import Base


class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    job_description = Column(String)

    candidate_skills = Column(String)

    match_score = Column(Integer)

    ai_summary = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )