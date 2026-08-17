from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.job_models import JobRequest
from app.models.analysis_model import Analysis
from app.models.user_model import User

from app.database.database import get_db

from app.dependencies.auth_dependencies import (
    get_current_user
)

from app.services.analysis_service import (
    analyze_job_for_user
)

router = APIRouter()

@router.post("/analyze-job")
def analyze_job(
    job: JobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return analyze_job_for_user(
        job_description=job.job_description,
        candidate_skills=job.candidate_skills,
        user_id=current_user.id,
        db=db
    )

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