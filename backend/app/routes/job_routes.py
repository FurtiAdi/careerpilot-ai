import tempfile
import shutil
import os

from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.services.resume_service import extract_text_from_pdf
from app.models.job_models import JobRequest
from app.services.ai_service import generate_ai_analysis
from uuid import uuid4

from app.services.job_service import (
    extract_skills,
    calculate_match_score
)

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.analysis_model import Analysis

from app.models.user_model import User
from app.models.user_schema import UserCreate, UserLogin

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

from app.dependencies.auth_dependencies import (
    get_current_user
)

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(await file.read())

        temp_file_path = temp_file.name

    extracted_text = extract_text_from_pdf(
        temp_file_path
    )

    detected_skills = extract_skills(
        extracted_text
    )

    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "detected_skills": detected_skills
    }

