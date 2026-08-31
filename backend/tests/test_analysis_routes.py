from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.job_models import JobRequest
from app.routes import analysis_routes


def test_analyze_job_calls_service(monkeypatch):
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 7

    job = JobRequest(
        job_description="Python FastAPI role",
        candidate_skills=["Python", "FastAPI"],
    )

    expected_result = {
        "match_analysis": {
            "match_score": 80
        }
    }

    mock_service = MagicMock(
        return_value=expected_result
    )

    monkeypatch.setattr(
        analysis_routes,
        "analyze_job_for_user",
        mock_service,
    )

    result = analysis_routes.analyze_job(
        job=job,
        db=mock_db,
        current_user=mock_user,
    )

    assert result == expected_result

    mock_service.assert_called_once_with(
        job_description="Python FastAPI role",
        candidate_skills=["Python", "FastAPI"],
        user_id=7,
        db=mock_db,
    )


def test_get_analyses_uses_current_user(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 4

    expected = [
        MagicMock(),
        MagicMock(),
    ]

    mock_service = MagicMock(
        return_value=expected
    )

    monkeypatch.setattr(
        analysis_routes,
        "get_user_analyses",
        mock_service,
    )

    result = analysis_routes.get_analyses(
        db=mock_db,
        current_user=mock_user,
    )

    assert result == expected

    mock_service.assert_called_once_with(
        user_id=4,
        db=mock_db,
    )


def test_delete_analysis_success(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 3

    mock_analysis = MagicMock()

    mock_service = MagicMock(
        return_value=mock_analysis
    )

    monkeypatch.setattr(
        analysis_routes,
        "delete_user_analysis",
        mock_service,
    )

    result = analysis_routes.delete_analysis(
        analysis_id=10,
        db=mock_db,
        current_user=mock_user,
    )

    assert result == {
        "message": "Analysis deleted"
    }

    mock_service.assert_called_once_with(
        analysis_id=10,
        user_id=3,
        db=mock_db,
    )


def test_delete_analysis_returns_404_when_missing(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 3

    monkeypatch.setattr(
        analysis_routes,
        "delete_user_analysis",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        analysis_routes.delete_analysis(
            analysis_id=999,
            db=mock_db,
            current_user=mock_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Analysis not found"
    )