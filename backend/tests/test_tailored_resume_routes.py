from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.tailored_resume_schema import (
    TailoredResumeGenerateRequest,
)
from app.routes import tailored_resume_routes
from app.services.ai_service import (
    TailoredResumeGenerationError,
)
from app.services.tailored_resume_service import (
    TailoredResumeGroundingError,
    TailoredResumeSourceError,
)


client = TestClient(app)


def make_request() -> TailoredResumeGenerateRequest:
    return TailoredResumeGenerateRequest(
        analysis_id=12,
        source_content={
            "contact": {
                "full_name": "Ada Lovelace",
            },
            "skills": ["Python"],
        },
    )


def test_generate_tailored_resume_requires_authentication():
    response = client.post(
        "/tailored-resumes",
        json={
            "analysis_id": 12,
            "source_content": {
                "contact": {
                    "full_name": "Ada Lovelace",
                }
            },
        },
    )

    assert response.status_code == 401


def test_generate_tailored_resume_calls_scoped_service(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    generated_resume = MagicMock()

    mock_service = MagicMock(
        return_value=generated_resume
    )
    monkeypatch.setattr(
        tailored_resume_routes,
        "create_tailored_resume_for_user",
        mock_service,
    )

    result = (
        tailored_resume_routes
        .generate_tailored_resume_draft(
            request=make_request(),
            db=db,
            current_user=user,
        )
    )

    assert result is generated_resume
    mock_service.assert_called_once_with(
        analysis_id=12,
        source_content=make_request().source_content,
        current_user=user,
        db=db,
    )


def test_generate_tailored_resume_returns_404_for_missing_analysis(
    monkeypatch,
):
    monkeypatch.setattr(
        tailored_resume_routes,
        "create_tailored_resume_for_user",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        (
            tailored_resume_routes
            .generate_tailored_resume_draft(
                request=make_request(),
                db=MagicMock(),
                current_user=MagicMock(),
            )
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Analysis not found."


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (
            TailoredResumeSourceError("Missing resume"),
            422,
        ),
        (
            TailoredResumeGenerationError("Provider failure"),
            503,
        ),
        (
            TailoredResumeGroundingError("Unsafe response"),
            502,
        ),
    ],
)
def test_generate_tailored_resume_maps_service_errors(
    monkeypatch,
    service_error,
    expected_status,
):
    monkeypatch.setattr(
        tailored_resume_routes,
        "create_tailored_resume_for_user",
        MagicMock(side_effect=service_error),
    )

    with pytest.raises(HTTPException) as exc:
        (
            tailored_resume_routes
            .generate_tailored_resume_draft(
                request=make_request(),
                db=MagicMock(),
                current_user=MagicMock(),
            )
        )

    assert exc.value.status_code == expected_status