from unittest.mock import MagicMock

import pytest

from app.models.ai_schema import AIAnalysisResponse
from app.services import analysis_service


def test_analyze_job_for_user_success(monkeypatch):
    mock_db = MagicMock()

    mock_requirements = MagicMock()
    mock_requirements.required = ["python", "fastapi"]
    mock_requirements.preferred = ["docker"]

    monkeypatch.setattr(
        analysis_service,
        "classify_skill_requirements",
        MagicMock(return_value=mock_requirements),
    )

    score_results = {
        "match_score": 80,
        "required_score": 100,
        "preferred_score": 0,
        "matched_required_skills": [
            "python",
            "fastapi",
        ],
        "missing_required_skills": [],
        "matched_preferred_skills": [],
        "missing_preferred_skills": [
            "docker",
        ],
        "weights": {
            "required": 0.8,
            "preferred": 0.2,
        },
    }

    monkeypatch.setattr(
        analysis_service,
        "calculate_match_score",
        MagicMock(return_value=score_results),
    )

    ai_result = AIAnalysisResponse(
        summary="Strong match.",
        strengths=["Python"],
        missing_requirements=["Docker"],
        recommendations=["Learn Docker"],
    )

    monkeypatch.setattr(
        analysis_service,
        "generate_ai_analysis",
        MagicMock(return_value=ai_result),
    )

    result = analysis_service.analyze_job_for_user(
        job_description="Python FastAPI job",
        candidate_skills=["Python", "FastAPI"],
        user_id=1,
        db=mock_db,
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result["job_description"] == "Python FastAPI job"
    assert result["candidate_skills"] == [
        "Python",
        "FastAPI",
    ]
    assert result["match_analysis"] == score_results
    assert result["ai_analysis"] == ai_result


def test_analyze_job_for_user_rolls_back_on_commit_error(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_db.commit.side_effect = Exception(
        "Database error"
    )

    mock_requirements = MagicMock()
    mock_requirements.required = ["python"]
    mock_requirements.preferred = []

    monkeypatch.setattr(
        analysis_service,
        "classify_skill_requirements",
        MagicMock(return_value=mock_requirements),
    )

    monkeypatch.setattr(
        analysis_service,
        "calculate_match_score",
        MagicMock(
            return_value={
                "match_score": 80,
                "required_score": 100,
                "preferred_score": 0,
                "matched_required_skills": [
                    "python"
                ],
                "missing_required_skills": [],
                "matched_preferred_skills": [],
                "missing_preferred_skills": [],
                "weights": {
                    "required": 0.8,
                    "preferred": 0.2,
                },
            }
        ),
    )

    monkeypatch.setattr(
        analysis_service,
        "generate_ai_analysis",
        MagicMock(
            return_value=AIAnalysisResponse(
                summary="Good match."
            )
        ),
    )

    with pytest.raises(
        Exception,
        match="Database error",
    ):
        analysis_service.analyze_job_for_user(
            job_description="Python job",
            candidate_skills=["Python"],
            user_id=1,
            db=mock_db,
        )

    mock_db.rollback.assert_called_once()


def test_get_user_analyses_filters_by_user():
    mock_db = MagicMock()

    expected = [
        MagicMock(),
        MagicMock(),
    ]

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = expected

    result = analysis_service.get_user_analyses(
        user_id=7,
        db=mock_db,
    )

    assert result == expected
    mock_db.query.assert_called_once()


def test_delete_user_analysis_success():
    mock_db = MagicMock()

    analysis = MagicMock()

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = analysis

    result = analysis_service.delete_user_analysis(
        analysis_id=10,
        user_id=3,
        db=mock_db,
    )

    assert result == analysis
    mock_db.delete.assert_called_once_with(
        analysis
    )
    mock_db.commit.assert_called_once()


def test_delete_user_analysis_returns_none_when_missing():
    mock_db = MagicMock()

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    result = analysis_service.delete_user_analysis(
        analysis_id=999,
        user_id=3,
        db=mock_db,
    )

    assert result is None
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()


def test_delete_user_analysis_rolls_back_on_commit_error():
    mock_db = MagicMock()

    analysis = MagicMock()

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = analysis

    mock_db.commit.side_effect = Exception(
        "Database error"
    )

    with pytest.raises(
        Exception,
        match="Database error",
    ):
        analysis_service.delete_user_analysis(
            analysis_id=10,
            user_id=3,
            db=mock_db,
        )

    mock_db.rollback.assert_called_once()