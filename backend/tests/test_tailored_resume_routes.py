from unittest.mock import MagicMock

import pytest
from app.services.tailored_resume_service import TailoredResumeGroundingError
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.tailored_resume_schema import (
    TailoredResumeGenerateRequest,
    TailoredResumeUpdateRequest,
)
from app.routes import tailored_resume_routes
from app.services.ai_service import (
    TailoredResumeGenerationError,
)

from app.services.resume_service import (
    ResumeEvidenceError,
    SavedResumeNotFoundError,
)


client = TestClient(app)


def make_request() -> TailoredResumeGenerateRequest:
    return TailoredResumeGenerateRequest(
        analysis_id=12
    )


def test_generate_tailored_resume_requires_authentication():
    response = client.post(
        "/tailored-resumes",
        json={
            "analysis_id": 12,
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
            SavedResumeNotFoundError(),
            422,
        ),
        (
            ResumeEvidenceError(
                "content.experience[0].employer"
            ),
            502,
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


def test_list_tailored_resumes_requires_authentication():
    response = client.get("/tailored-resumes")

    assert response.status_code == 401


def test_list_tailored_resumes_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    expected = [MagicMock(), MagicMock()]

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        tailored_resume_routes,
        "get_user_tailored_resumes",
        mock_service,
    )

    result = tailored_resume_routes.list_tailored_resumes(
        db=db,
        current_user=user,
    )

    assert result == expected
    mock_service.assert_called_once_with(
        user_id=7,
        db=db,
    )


def test_get_tailored_resume_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    expected = MagicMock()

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        tailored_resume_routes,
        "get_user_tailored_resume",
        mock_service,
    )

    result = tailored_resume_routes.get_tailored_resume(
        tailored_resume_id=12,
        db=db,
        current_user=user,
    )

    assert result is expected
    mock_service.assert_called_once_with(
        tailored_resume_id=12,
        user_id=7,
        db=db,
    )


def test_get_tailored_resume_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        tailored_resume_routes,
        "get_user_tailored_resume",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        tailored_resume_routes.get_tailored_resume(
            tailored_resume_id=99,
            db=MagicMock(),
            current_user=MagicMock(id=7),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Tailored resume not found."
    )

@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("PATCH", {"status": "saved"}),
        ("DELETE", None),
    ],
)
def test_write_routes_require_authentication(
    method,
    payload,
):
    response = client.request(
        method,
        "/tailored-resumes/12",
        json=payload,
    )

    assert response.status_code == 401


def test_update_tailored_resume_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    expected = MagicMock()

    mock_service = MagicMock(return_value=expected)
    monkeypatch.setattr(
        tailored_resume_routes,
        "create_user_tailored_resume_version",
        mock_service,
    )

    request = TailoredResumeUpdateRequest(
        status="saved"
    )

    result = tailored_resume_routes.update_tailored_resume(
        tailored_resume_id=12,
        request=request,
        db=db,
        current_user=user,
    )

    assert result is expected
    mock_service.assert_called_once_with(
        tailored_resume_id=12,
        user_id=7,
        content=None,
        status="saved",
        db=db,
    )


def test_update_tailored_resume_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        tailored_resume_routes,
        "create_user_tailored_resume_version",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        tailored_resume_routes.update_tailored_resume(
            tailored_resume_id=99,
            request=TailoredResumeUpdateRequest(
                status="saved"
            ),
            db=MagicMock(),
            current_user=MagicMock(id=7),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Tailored resume not found."
    )


def test_delete_tailored_resume_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    deleted = MagicMock()

    mock_service = MagicMock(return_value=deleted)
    monkeypatch.setattr(
        tailored_resume_routes,
        "delete_user_tailored_resume",
        mock_service,
    )

    result = tailored_resume_routes.delete_tailored_resume(
        tailored_resume_id=12,
        db=db,
        current_user=user,
    )

    assert result == {
        "message": "Tailored resume deleted."
    }
    mock_service.assert_called_once_with(
        tailored_resume_id=12,
        user_id=7,
        db=db,
    )


def test_delete_tailored_resume_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        tailored_resume_routes,
        "delete_user_tailored_resume",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        tailored_resume_routes.delete_tailored_resume(
            tailored_resume_id=99,
            db=MagicMock(),
            current_user=MagicMock(id=7),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Tailored resume not found."
    )
