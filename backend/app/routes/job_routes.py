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


@router.post("/analyze-job")
def analyze_job(
    job: JobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

        user_id=current_user.id,

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).all()

    return analyses

@router.delete("/analyses/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
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

# User Registration Routes
@router.post("/register")
def register_user(

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    resume: UploadFile = File(None),

    profile_picture: UploadFile = File(None),

    db: Session = Depends(get_db)

    ):

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:

        return {
            "error": "Email already exists"
        }

    hashed_password = hash_password(password)

    resume_filename = None

    profile_picture_filename = None

    if resume:

        resume_filename = resume.filename

        with open(
            f"uploads/resumes/{resume_filename}",
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                resume.file,
                buffer
            )
    if profile_picture:

        profile_picture_filename = profile_picture.filename

        with open(
            f"uploads/profile_pictures/{profile_picture_filename}",
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                profile_picture.file,
                buffer
            )

    new_user = User(

        full_name=full_name,

        email=email,

        hashed_password=hashed_password,

        resume_filename=resume_filename,

        profile_picture_filename=profile_picture_filename
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login_user(
    user: UserLogin,
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