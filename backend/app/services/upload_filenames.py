from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


PROFILE_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def generate_profile_picture_filename(
    file: UploadFile,
) -> str:
    content_type = file.content_type or ""

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