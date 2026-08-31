import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    # Database
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    DATABASE_URL = (
        f"postgresql://"
        f"{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/"
        f"{POSTGRES_DB}"
    )

    # Authentication
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_ANALYSIS_MODEL = "gpt-4.1-mini"

    # Uploads
    PROFILE_PICTURE_DIR = (
        "uploads/profile_pictures"
    )
    RESUME_DIR = "uploads/resumes"

    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


settings = Settings()