from pathlib import Path

from fastapi import HTTPException, UploadFile, status


MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024


async def read_validated_pdf(
    file: UploadFile,
) -> bytes:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Resume uploads must be PDF files.",
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Resume uploads must use application/pdf.",
        )

    content = await file.read(
        MAX_RESUME_SIZE_BYTES + 1
    )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded resume is empty.",
        )

    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume uploads must not exceed 5 MiB.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded file is not a valid PDF.",
        )

    return content