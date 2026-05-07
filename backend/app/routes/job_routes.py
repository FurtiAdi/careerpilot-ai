from fastapi import APIRouter
from app.models.job_models import JobRequest
from app.services.job_service import extract_skills

router = APIRouter()


@router.post("/analyze-job")
def analyze_job(job: JobRequest):
    description = job.job_description
    skills = extract_skills(description)

    return {
        "job_description": description,
        "detected_skills": skills,
        "total_skills_found": len(skills)
    }