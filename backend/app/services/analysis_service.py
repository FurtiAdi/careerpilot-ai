from sqlalchemy.orm import Session

from app.models.analysis_model import Analysis

from app.services.ai_service import (
    generate_ai_analysis
)

from app.skills.requirements import (
    classify_skill_requirements
)

from app.skills.scorer import (
    calculate_match_score
)


def analyze_job_for_user(
    job_description: str,
    candidate_skills: list[str],
    user_id: int,
    db: Session
):

    requirements = classify_skill_requirements(
        job_description
    )

    score_results = calculate_match_score(
        required_skills=requirements.required,
        preferred_skills=requirements.preferred,
        candidate_skills=candidate_skills
    )

    ai_analysis = generate_ai_analysis(
        match_score=score_results["match_score"],
        matched_required_skills=(
            score_results["matched_required_skills"]
        ),
        missing_required_skills=(
            score_results["missing_required_skills"]
        ),
        matched_preferred_skills=(
            score_results["matched_preferred_skills"]
        ),
        missing_preferred_skills=(
            score_results["missing_preferred_skills"]
        ),
    )

    new_analysis = Analysis(

        user_id=user_id,

        job_description=job_description,

        candidate_skills=", ".join(
            candidate_skills
        ),

        match_score=score_results["match_score"],

        ai_summary=ai_analysis.summary,
    )

    db.add(new_analysis)

    db.commit()

    db.refresh(new_analysis)

    return {
        "job_description": job_description,
        "detected_job_skills": {
            "required": requirements.required,
            "preferred": requirements.preferred
        },
        "candidate_skills": candidate_skills,
        "match_analysis": score_results,
        "ai_analysis": ai_analysis
    }

def get_user_analyses(
    user_id: int,
    db: Session
):

    return db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).all()


def delete_user_analysis(
    analysis_id: int,
    user_id: int,
    db: Session
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        return None

    db.delete(analysis)

    db.commit()

    return analysis