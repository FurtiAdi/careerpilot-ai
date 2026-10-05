from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.career_profile_schema import (
    CareerProfileExtractRequest,
)
from app.routes import career_profile_routes
from app.services.ai_service import (
    CareerProfileStructuringError,
)
from app.services.career_profile_service import (
    CareerProfileReviewedError,
)
from app.services.resume_service import (
    ResumeEvidenceError,
    SavedResumeNotFoundError,
)


client = TestClient(app)


def test_extract_career_profile_requires_authentication():
    response = client.post(
        "/career-profiles/extract",
        json={"source_resume_id": 21},
    )

    assert response.status_code == 401


def test_extract_career_profile_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock(id=7)
    expected = MagicMock()

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        career_profile_routes,
        "extract_and_persist_career_profile_for_user",
        mock_service,
    )

    result = career_profile_routes.extract_career_profile(
        request=CareerProfileExtractRequest(
            source_resume_id=21,
        ),
        db=db,
        current_user=user,
    )

    assert result is expected
    mock_service.assert_called_once_with(
        source_resume_id=21,
        user_id=7,
        db=db,
    )


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (
            SavedResumeNotFoundError(),
            422,
        ),
        (
            CareerProfileStructuringError(
                "Provider unavailable"
            ),
            503,
        ),
        (
            ResumeEvidenceError("content.skills[0]"),
            502,
        ),
        (
            CareerProfileReviewedError(
                "Reviewed profile"
            ),
            409,
        ),
    ],
)
def test_extract_career_profile_maps_service_errors(
    monkeypatch,
    service_error,
    expected_status,
):
    monkeypatch.setattr(
        career_profile_routes,
        "extract_and_persist_career_profile_for_user",
        MagicMock(side_effect=service_error),
    )

    with pytest.raises(HTTPException) as exc:
        career_profile_routes.extract_career_profile(
            request=CareerProfileExtractRequest(
                source_resume_id=21,
            ),
            db=MagicMock(),
            current_user=MagicMock(id=7),
        )

    assert exc.value.status_code == expected_status


def test_get_current_career_profile_requires_authentication():
    response = client.get("/career-profiles/me")

    assert response.status_code == 401


def test_get_current_career_profile_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock(id=7)
    expected = MagicMock()

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        career_profile_routes,
        "get_user_career_profile",
        mock_service,
    )

    result = (
        career_profile_routes.get_current_career_profile(
            db=db,
            current_user=user,
        )
    )

    assert result is expected
    mock_service.assert_called_once_with(
        user_id=7,
        db=db,
    )


def test_get_current_career_profile_returns_404_when_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        career_profile_routes,
        "get_user_career_profile",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        career_profile_routes.get_current_career_profile(
            db=MagicMock(),
            current_user=MagicMock(id=7),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Career Profile not found."