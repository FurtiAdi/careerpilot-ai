import io

import pytest
from fastapi import HTTPException, UploadFile

from app.services.upload_validation import (
    MAX_PROFILE_IMAGE_SIZE_BYTES,
    read_validated_profile_image,
)


def create_upload_file(
    filename: str,
    content: bytes,
    content_type: str,
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={
            "content-type": content_type,
        },
    )


@pytest.mark.anyio
async def test_valid_jpeg_is_accepted():
    content = b"fake-jpeg-content"

    file = create_upload_file(
        "profile.jpg",
        content,
        "image/jpeg",
    )

    result = await read_validated_profile_image(file)

    assert result == content


@pytest.mark.anyio
async def test_valid_png_is_accepted():
    content = b"fake-png-content"

    file = create_upload_file(
        "profile.png",
        content,
        "image/png",
    )

    result = await read_validated_profile_image(file)

    assert result == content


@pytest.mark.anyio
async def test_valid_webp_is_accepted():
    content = b"fake-webp-content"

    file = create_upload_file(
        "profile.webp",
        content,
        "image/webp",
    )

    result = await read_validated_profile_image(file)

    assert result == content


@pytest.mark.anyio
async def test_unsupported_image_type_is_rejected():
    file = create_upload_file(
        "profile.gif",
        b"gif-content",
        "image/gif",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_profile_image(file)

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_empty_profile_image_is_rejected():
    file = create_upload_file(
        "profile.jpg",
        b"",
        "image/jpeg",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_profile_image(file)

    assert exc.value.status_code == 422


@pytest.mark.anyio
async def test_oversized_profile_image_is_rejected():
    content = (
        b"x"
        * (MAX_PROFILE_IMAGE_SIZE_BYTES + 1)
    )

    file = create_upload_file(
        "profile.jpg",
        content,
        "image/jpeg",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_profile_image(file)

    assert exc.value.status_code == 413