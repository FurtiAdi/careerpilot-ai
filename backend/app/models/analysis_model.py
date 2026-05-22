from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime

from app.database.database import Base


class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_description = Column(Text)

    candidate_skills = Column(Text)

    match_score = Column(Integer)

    ai_summary = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)