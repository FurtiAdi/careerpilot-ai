import io

import pytest
from fastapi import HTTPException, UploadFile

from app.services.upload_validation import (
    MAX_RESUME_SIZE_BYTES,
    read_validated_pdf,
)


def create_upload_file(
    filename: str,
    content: bytes,
    content_type: str = "application/pdf",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={
            "content-type": content_type,
        },
    )


@pytest.mark.anyio
async def test_valid_pdf_is_accepted():
    content = b"%PDF-1.4 test pdf content"

    file = create_upload_file(
        "resume.pdf",
        content,
    )

    result = await read_validated_pdf(file)

    assert result == content


@pytest.mark.anyio
async def test_wrong_extension_is_rejected():
    file = create_upload_file(
        "resume.txt",
        b"%PDF-1.4 test content",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_pdf(file)

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_wrong_content_type_is_rejected():
    file = create_upload_file(
        "resume.pdf",
        b"%PDF-1.4 test content",
        content_type="text/plain",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_pdf(file)

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_empty_pdf_is_rejected():
    file = create_upload_file(
        "resume.pdf",
        b"",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_pdf(file)

    assert exc.value.status_code == 422


@pytest.mark.anyio
async def test_oversized_pdf_is_rejected():
    content = (
        b"%PDF-"
        + b"x" * MAX_RESUME_SIZE_BYTES
    )

    file = create_upload_file(
        "resume.pdf",
        content,
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_pdf(file)

    assert exc.value.status_code == 413


@pytest.mark.anyio
async def test_fake_pdf_is_rejected():
    file = create_upload_file(
        "resume.pdf",
        b"This is not really a PDF.",
    )

    with pytest.raises(HTTPException) as exc:
        await read_validated_pdf(file)

    assert exc.value.status_code == 422