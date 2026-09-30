from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes import saved_resume_routes


client = TestClient(app)


def test_list_saved_resumes_requires_authentication():
    response = client.get("/saved-resumes")

    assert response.status_code == 401


def test_list_saved_resumes_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock(id=7)
    expected = [MagicMock(), MagicMock()]

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        saved_resume_routes,
        "get_user_saved_resumes",
        mock_service,
    )

    result = saved_resume_routes.list_saved_resumes(
        db=db,
        current_user=user,
    )

    assert result == expected
    mock_service.assert_called_once_with(
        user_id=7,
        db=db,
    )


def test_upload_saved_resume_requires_authentication():
    response = client.post(
        "/saved-resumes",
        files={
            "file": (
                "my-resume.pdf",
                b"%PDF-1.4 test resume",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_upload_saved_resume_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock(id=7)
    uploaded_file = MagicMock()
    uploaded_file.filename = "my-resume.pdf"
    expected = MagicMock()

    async def mock_validation(file):
        assert file is uploaded_file
        return b"%PDF-1.4 test resume"

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        saved_resume_routes,
        "read_validated_pdf",
        mock_validation,
    )
    monkeypatch.setattr(
        saved_resume_routes,
        "create_saved_resume",
        mock_service,
    )

    result = await saved_resume_routes.upload_saved_resume(
        file=uploaded_file,
        db=db,
        current_user=user,
    )

    assert result is expected
    mock_service.assert_called_once_with(
        user_id=7,
        original_filename="my-resume.pdf",
        content=b"%PDF-1.4 test resume",
        db=db,
    )
