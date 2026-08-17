from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.job_models import JobRequest
from app.models.analysis_model import Analysis
from app.models.user_model import User

from app.database.database import get_db

from app.dependencies.auth_dependencies import (
    get_current_user
)

from app.services.ai_service import (
    generate_ai_analysis
)

from app.services.job_service import (
    extract_skills,
    calculate_match_score
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

    extracted_skills = extract_skills(
        description
    )

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