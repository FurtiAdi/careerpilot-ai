from uuid import uuid4

from fastapi import HTTPException, status


PROFILE_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def generate_profile_picture_filename(
    content_type: str,
) -> str:
    extension = PROFILE_IMAGE_EXTENSIONS.get(
        content_type
    )

    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Profile pictures must be JPEG, PNG, "
                "or WebP images."
            ),
        )

    return f"{uuid4()}{extension}"


def generate_resume_filename() -> str:
    return f"{uuid4()}.pdf"