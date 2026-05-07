from fastapi import APIRouter

from app.models.job_models import JobRequest

from app.services.job_service import (
    extract_skills,
    calculate_match_score
)

router = APIRouter()


@router.post("/analyze-job")
def analyze_job(job: JobRequest):

    description = job.job_description

    candidate_skills = job.candidate_skills

    extracted_skills = extract_skills(description)

    score_results = calculate_match_score(
        extracted_skills,
        candidate_skills
    )

    return {
        "job_description": description,
        "detected_job_skills": extracted_skills,
        "candidate_skills": candidate_skills,
        "match_analysis": score_results
    }