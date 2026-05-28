from fastapi import APIRouter, UploadFile, File
import tempfile

from app.services.resume_service import extract_text_from_pdf
from app.models.job_models import JobRequest
from app.services.ai_service import generate_ai_analysis

from app.services.job_service import (
    extract_skills,
    calculate_match_score
)
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.analysis_model import Analysis

from app.models.user_model import User
from app.models.user_schema import UserCreate

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token     
)

router = APIRouter()


@router.post("/analyze-job")
def analyze_job(
    job: JobRequest,
    db: Session = Depends(get_db)
):

    description = job.job_description

    candidate_skills = job.candidate_skills

    ai_analysis = generate_ai_analysis(
        description,
        candidate_skills
    )

    extracted_skills = extract_skills(description)

    score_results = calculate_match_score(
        extracted_skills,
        candidate_skills
    )

    new_analysis = Analysis(

        job_description=description,

        candidate_skills=", ".join(
            candidate_skills
        ),

        match_score=score_results["match_score"],

        ai_summary=ai_analysis["summary"]
    )

    db.add(new_analysis)

    db.commit()

    db.refresh(new_analysis)

    return {
        "job_description": description,
        "detected_job_skills": extracted_skills,
        "candidate_skills": candidate_skills,
        "match_analysis": score_results,
        "ai_analysis": ai_analysis
    }

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

@router.get("/analyses")
def get_analyses(
    db: Session = Depends(get_db)
):

    analyses = db.query(Analysis).all()

    return analyses

@router.delete("/analyses/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if not analysis:
        return {
            "error": "Analysis not found"
        }

    db.delete(analysis)

    db.commit()

    return {
        "message": "Analysis deleted"
    }

@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        return {
            "error": "Email already exists"
        }

    hashed_password = hash_password(
        user.password
    )

    new_user = User(

        email=user.email,

        hashed_password=hashed_password
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
def login_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        return {
            "error": "Invalid email or password"
        }

    valid_password = verify_password(
        user.password,
        existing_user.hashed_password
    )

    if not valid_password:

        return {
            "error": "Invalid email or password"
        }

    access_token = create_access_token(
        data={
            "sub": existing_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }