import os
import tempfile

from fastapi import APIRouter, File, UploadFile

from app.services.job_service import extract_skills
from app.services.resume_service import extract_text_from_pdf
from app.services.upload_validation import read_validated_pdf


router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):
    file_content = await read_validated_pdf(file)
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(file_content)
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
            "detected_skills": detected_skills,
        }

    finally:
        if (
            temp_file_path
            and os.path.exists(temp_file_path)
        ):
            os.remove(temp_file_path)
            