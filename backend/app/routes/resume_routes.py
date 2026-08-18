import tempfile

from fastapi import APIRouter, UploadFile, File

from app.services.resume_service import (
    extract_text_from_pdf
)

from app.services.job_service import (
    extract_skills
)


router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(
            await file.read()
        )

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