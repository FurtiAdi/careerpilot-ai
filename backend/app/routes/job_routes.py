from fastapi import APIRouter, UploadFile, File
import tempfile

from app.services.resume_service import extract_text_from_pdf
from app.models.job_models import JobRequest
from app.services.ai_service import generate_ai_analysis

from app.services.job_service import (
    extract_skills,
    calculate_match_score
)

router = APIRouter()


@router.post("/analyze-job")
def analyze_job(job: JobRequest):

    description = job.job_description

    ai_analysis = generate_ai_analysis(description)

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

    return {
        "filename": file.filename,
        "extracted_text": extracted_text
    }