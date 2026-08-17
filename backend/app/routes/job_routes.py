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

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "resume_filename": current_user.resume_filename,
        "profile_picture_filename": current_user.profile_picture_filename
    }

@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    upload_dir = "uploads/profile_pictures"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_extension = (
        file.filename.split(".")[-1]
    )

    unique_filename = (
        f"{uuid4()}.{file_extension}"
    )

    file_path = (
        f"{upload_dir}/{unique_filename}"
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    current_user.profile_picture_filename = (
        unique_filename
    )

    db.commit()

    return {
        "profile_picture_filename":
        unique_filename
    }

@router.get("/profile-stats")
def get_profile_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).all()

    total_analyses = len(analyses)

    average_score = 0

    if total_analyses > 0:

        average_score = round(
            sum(
                analysis.match_score
                for analysis in analyses
            ) / total_analyses
        )

    return {
        "total_analyses": total_analyses,
        "average_match_score": average_score,
        "resume_uploaded": bool(
            current_user.resume_filename
        )
    }