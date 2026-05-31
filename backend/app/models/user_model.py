from sqlalchemy import (
    Column,
    Integer,
    String
)

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    
    full_name = Column(String)

    profile_picture = Column(String, nullable=True)

    resume_filename = Column(String, nullable=True)


    email = Column(
        String,
        unique=True,
        index=True
    )

    hashed_password = Column(String)