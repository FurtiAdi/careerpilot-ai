import pytest

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.skills.requirements import SkillRequirements
from app.services import tailored_resume_service

def make_grounding_source() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
        },
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
                "start_date": "2022",
                "end_date": "2024",
                "bullets": [
                    "Built Python applications."
                ],
            }
        ],
        skills=["Python"],
    )


def test_grounding_allows_rephrasing_of_real_experience():
    source = make_grounding_source()
    generated = source.model_copy(deep=True)
    generated.experience[0].bullets = [
        "Developed applications using Python."
    ]

    tailored_resume_service.validate_tailored_resume_grounding(
        source=source,
        generated=generated,
        match_snapshot={
            "missing_required_skills": ["docker"],
            "missing_preferred_skills": [],
        },
    )


def test_grounding_rejects_invented_employer():
    source = make_grounding_source()
    generated = source.model_copy(deep=True)
    generated.experience[0].employer = "Invented Company"

    with pytest.raises(
        tailored_resume_service.TailoredResumeGroundingError,
        match="unsupported facts",
    ):
        tailored_resume_service.validate_tailored_resume_grounding(
            source=source,
            generated=generated,
            match_snapshot={},
        )


def test_grounding_rejects_missing_skill_as_claimed():
    source = make_grounding_source()
    generated = source.model_copy(deep=True)
    generated.skills.append("Docker")

    with pytest.raises(
        tailored_resume_service.TailoredResumeGroundingError,
        match="unsupported skills",
    ):
        tailored_resume_service.validate_tailored_resume_grounding(
            source=source,
            generated=generated,
            match_snapshot={
                "missing_required_skills": ["docker"],
            },
        )


def test_grounding_rejects_invented_quantity():
    source = make_grounding_source()
    generated = source.model_copy(deep=True)
    generated.experience[0].bullets = [
        "Improved application performance by 50%."
    ]

    with pytest.raises(
        tailored_resume_service.TailoredResumeGroundingError,
        match="unsupported quantity",
    ):
        tailored_resume_service.validate_tailored_resume_grounding(
            source=source,
            generated=generated,
            match_snapshot={},
        )
        

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