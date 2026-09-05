from types import SimpleNamespace
from unittest.mock import MagicMock

from app.skills.requirements import SkillRequirements
from app.services import tailored_resume_service


def test_build_match_snapshot_uses_stored_analysis(
    monkeypatch,
):
    analysis = SimpleNamespace(
        job_description="Python role. Nice to have Docker.",
        candidate_skills="Python, FastAPI",
    )

    requirements = SkillRequirements(
        required=["python"],
        preferred=["docker"],
    )

    expected_snapshot = {
        "match_score": 80,
        "required_score": 100,
        "preferred_score": 0,
        "matched_required_skills": ["python"],
        "missing_required_skills": [],
        "matched_preferred_skills": [],
        "missing_preferred_skills": ["docker"],
        "weights": {
            "required": 0.8,
            "preferred": 0.2,
        },
    }

    mock_classify = MagicMock(
        return_value=requirements
    )
    mock_score = MagicMock(
        return_value=expected_snapshot
    )

    monkeypatch.setattr(
        tailored_resume_service,
        "classify_skill_requirements",
        mock_classify,
    )
    monkeypatch.setattr(
        tailored_resume_service,
        "calculate_match_score",
        mock_score,
    )

    result = (
        tailored_resume_service
        .build_analysis_match_snapshot(analysis)
    )

    assert result == expected_snapshot

    mock_classify.assert_called_once_with(
        analysis.job_description
    )
    mock_score.assert_called_once_with(
        required_skills=["python"],
        preferred_skills=["docker"],
        candidate_skills=["Python", "FastAPI"],
    )