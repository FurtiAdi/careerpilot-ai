from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

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