from pathlib import Path

from fastapi import HTTPException, UploadFile, status


MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024
MAX_PROFILE_IMAGE_SIZE_BYTES = 2 * 1024 * 1024

ALLOWED_PROFILE_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


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

async def read_validated_profile_image(
    file: UploadFile,
) -> bytes:
    content_type = file.content_type or ""

    if content_type not in ALLOWED_PROFILE_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Profile pictures must be JPEG, PNG, "
                "or WebP images."
            ),
        )

    content = await file.read(
        MAX_PROFILE_IMAGE_SIZE_BYTES + 1
    )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded image is empty.",
        )

    if len(content) > MAX_PROFILE_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Profile pictures must not exceed 2 MiB.",
        )

    if content_type == "image/jpeg":
        is_valid_image = content.startswith(
            b"\xff\xd8\xff"
        )

    elif content_type == "image/png":
        is_valid_image = content.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    elif content_type == "image/webp":
        is_valid_image = (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        )

    else:
        is_valid_image = False

    if not is_valid_image:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded file is not a valid image.",
        )



    return content