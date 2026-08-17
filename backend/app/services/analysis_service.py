from sqlalchemy.orm import Session

from app.models.analysis_model import Analysis
from app.services.ai_service import generate_ai_analysis
from app.services.job_service import (
    extract_skills,
    calculate_match_score
)


def analyze_job_for_user(
    job_description: str,
    candidate_skills: list[str],
    user_id: int,
    db: Session
):

    ai_analysis = generate_ai_analysis(
        job_description,
        candidate_skills
    )

    extracted_skills = extract_skills(
        job_description
    )

    score_results = calculate_match_score(
        extracted_skills,
        candidate_skills
    )

    new_analysis = Analysis(

        user_id=user_id,

        job_description=job_description,

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
        "job_description": job_description,
        "detected_job_skills": extracted_skills,
        "candidate_skills": candidate_skills,
        "match_analysis": score_results,
        "ai_analysis": ai_analysis
    }