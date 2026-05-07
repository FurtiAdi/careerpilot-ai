from fastapi import APIRouter
from app.models.job_models import JobRequest

router = APIRouter()


@router.post("/analyze-job")
def analyze_job(job: JobRequest):
    description = job.job_description

    return {
        "received_job_description": description,
        "length": len(description)
    }