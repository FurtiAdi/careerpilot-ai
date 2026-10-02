from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.cover_letter_schema import (
    CoverLetterGenerateRequest,
    CoverLetterUpdateRequest,
)
from app.routes import cover_letter_routes
from app.services.ai_service import (
    CoverLetterGenerationError,
)
from app.services.cover_letter_service import (
    CoverLetterGroundingError,
)
from app.services.resume_service import (
    SavedResumeNotFoundError,
)


client = TestClient(app)


def make_request() -> CoverLetterGenerateRequest:
    return CoverLetterGenerateRequest(
        analysis_id=12,
        source_resume_id=21,
    )


def test_generate_cover_letter_requires_authentication():
    response = client.post(
        "/cover-letters",
        json={
            "analysis_id": 12,
            "source_resume_id": 21,
        },
    )

    assert response.status_code == 401


def test_generate_cover_letter_calls_scoped_service(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    generated_letter = MagicMock()

    mock_service = MagicMock(
        return_value=generated_letter
    )
    monkeypatch.setattr(
        cover_letter_routes,
        "create_cover_letter_for_user",
        mock_service,
    )

    result = (
        cover_letter_routes
        .generate_cover_letter_draft(
            request=make_request(),
            db=db,
            current_user=user,
        )
    )

    assert result is generated_letter
    mock_service.assert_called_once_with(
        analysis_id=12,
        source_resume_id=21,
        source_tailored_resume_id=None,
        tone="professional",
        length="standard",
        current_user=user,
        db=db,
    )


def test_generate_cover_letter_returns_404_for_missing_analysis(
    monkeypatch,
):
    monkeypatch.setattr(
        cover_letter_routes,
        "create_cover_letter_for_user",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        cover_letter_routes.generate_cover_letter_draft(
            request=make_request(),
            db=MagicMock(),
            current_user=MagicMock(),
        )

    assert exc.value.status_code == 404


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (SavedResumeNotFoundError(), 422),
        (ValueError("Missing tailored resume"), 422),
        (CoverLetterGenerationError("Provider failure"), 503),
        (CoverLetterGroundingError("Unsafe content"), 502),
    ],
)
def test_generate_cover_letter_maps_service_errors(
    monkeypatch,
    service_error,
    expected_status,
):
    monkeypatch.setattr(
        cover_letter_routes,
        "create_cover_letter_for_user",
        MagicMock(side_effect=service_error),
    )

    with pytest.raises(HTTPException) as exc:
        cover_letter_routes.generate_cover_letter_draft(
            request=make_request(),
            db=MagicMock(),
            current_user=MagicMock(),
        )

    assert exc.value.status_code == expected_status


def test_list_cover_letters_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    expected = [MagicMock()]

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        cover_letter_routes,
        "get_user_cover_letters",
        mock_service,
    )

    result = cover_letter_routes.list_cover_letters(
        db=db,
        current_user=user,
    )

    assert result == expected
    mock_service.assert_called_once_with(
        user_id=7,
        db=db,
    )


def test_get_cover_letter_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        cover_letter_routes,
        "get_user_cover_letter",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        cover_letter_routes.get_cover_letter(
            cover_letter_id=99,
            db=MagicMock(),
            current_user=MagicMock(),
        )

    assert exc.value.status_code == 404


def test_update_cover_letter_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    updated_letter = MagicMock()

    mock_service = MagicMock(return_value=updated_letter)
    monkeypatch.setattr(
        cover_letter_routes,
        "create_user_cover_letter_version",
        mock_service,
    )

    request = CoverLetterUpdateRequest(status="saved")

    result = cover_letter_routes.update_cover_letter(
        cover_letter_id=12,
        request=request,
        db=db,
        current_user=user,
    )

    assert result is updated_letter
    mock_service.assert_called_once_with(
        cover_letter_id=12,
        user_id=7,
        content=None,
        status="saved",
        db=db,
    )


def test_regenerate_cover_letter_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    regenerated_letter = MagicMock()

    mock_service = MagicMock(
        return_value=regenerated_letter
    )
    monkeypatch.setattr(
        cover_letter_routes,
        "regenerate_user_cover_letter",
        mock_service,
    )

    result = cover_letter_routes.regenerate_cover_letter(
        cover_letter_id=12,
        db=db,
        current_user=user,
    )

    assert result is regenerated_letter
    mock_service.assert_called_once_with(
        cover_letter_id=12,
        user_id=7,
        db=db,
    )


def test_write_routes_require_authentication():
    update_response = client.patch(
        "/cover-letters/12",
        json={"status": "saved"},
    )
    delete_response = client.delete("/cover-letters/12")

    assert update_response.status_code == 401
    assert delete_response.status_code == 401


def test_export_cover_letter_requires_authentication():
    response = client.get("/cover-letters/12/export")

    assert response.status_code == 401


def test_export_cover_letter_uses_scoped_cover_letter(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    cover_letter = MagicMock()
    cover_letter.id = 12
    cover_letter.content = {
        "opening": "I am applying for the role.",
        "evidence": [],
        "motivation": "The role aligns with my experience.",
        "closing": "Thank you.",
    }

    mock_get = MagicMock(return_value=cover_letter)
    monkeypatch.setattr(
        cover_letter_routes,
        "get_user_cover_letter",
        mock_get,
    )
    monkeypatch.setattr(
        cover_letter_routes,
        "render_cover_letter_pdf",
        MagicMock(return_value=b"%PDF-test"),
    )

    response = cover_letter_routes.export_cover_letter(
        cover_letter_id=12,
        db=db,
        current_user=user,
    )

    assert response.body == b"%PDF-test"
    assert response.media_type == "application/pdf"
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="cover-letter-12.pdf"'
    )
    mock_get.assert_called_once_with(
        cover_letter_id=12,
        user_id=7,
        db=db,
    )


def test_export_cover_letter_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        cover_letter_routes,
        "get_user_cover_letter",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        cover_letter_routes.export_cover_letter(
            cover_letter_id=99,
            db=MagicMock(),
            current_user=MagicMock(),
        )

    assert exc.value.status_code == 404
