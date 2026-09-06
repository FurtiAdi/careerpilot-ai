import pytest

from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
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


def test_create_tailored_resume_persists_grounded_result(
    monkeypatch,
):
    db = MagicMock()
    user = SimpleNamespace(
        id=7,
        resume_filename="saved-resume.pdf",
    )
    analysis = SimpleNamespace(
        id=12,
        user_id=7,
        job_description="Python role",
        candidate_skills="Python",
    )

    db.query.return_value.filter.return_value.first.return_value = (
        analysis
    )

    source = make_grounding_source()
    generated = TailoredResumeAIResponse(
        content=source,
        emphasized_items=["Python"],
        reordered_items=["Experience"],
    )
    snapshot = {
        "match_score": 80,
        "missing_required_skills": [],
        "missing_preferred_skills": [],
    }

    monkeypatch.setattr(
        tailored_resume_service,
        "build_analysis_match_snapshot",
        MagicMock(return_value=snapshot),
    )
    monkeypatch.setattr(
        tailored_resume_service,
        "generate_tailored_resume",
        MagicMock(return_value=generated),
    )
    mock_validate = MagicMock()
    monkeypatch.setattr(
        tailored_resume_service,
        "validate_tailored_resume_grounding",
        mock_validate,
    )

    result = (
        tailored_resume_service
        .create_tailored_resume_for_user(
            analysis_id=12,
            source_content=source,
            current_user=user,
            db=db,
        )
    )

    assert result.user_id == 7
    assert result.source_analysis_id == 12
    assert result.source_resume_filename == (
        "saved-resume.pdf"
    )
    assert result.content == source.model_dump(
        mode="json"
    )
    assert result.emphasized_items == ["Python"]
    assert result.reordered_items == ["Experience"]
    assert result.match_snapshot == snapshot

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

    mock_validate.assert_called_once_with(
        source=source,
        generated=generated.content,
        match_snapshot=snapshot,
    )


def test_create_tailored_resume_rejects_non_owned_analysis(
    monkeypatch,
):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (
        None
    )

    mock_generate = MagicMock()
    monkeypatch.setattr(
        tailored_resume_service,
        "generate_tailored_resume",
        mock_generate,
    )

    result = (
        tailored_resume_service
        .create_tailored_resume_for_user(
            analysis_id=99,
            source_content=make_grounding_source(),
            current_user=SimpleNamespace(
                id=7,
                resume_filename="saved-resume.pdf",
            ),
            db=db,
        )
    )

    assert result is None
    mock_generate.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_create_tailored_resume_rolls_back_on_commit_error(
    monkeypatch,
):
    db = MagicMock()
    db.commit.side_effect = Exception(
        "Database error"
    )

    user = SimpleNamespace(
        id=7,
        resume_filename="saved-resume.pdf",
    )
    analysis = SimpleNamespace(
        id=12,
        user_id=7,
        job_description="Python role",
        candidate_skills="Python",
    )

    db.query.return_value.filter.return_value.first.return_value = (
        analysis
    )

    source = make_grounding_source()
    generated = TailoredResumeAIResponse(
        content=source
    )

    monkeypatch.setattr(
        tailored_resume_service,
        "build_analysis_match_snapshot",
        MagicMock(return_value={}),
    )
    monkeypatch.setattr(
        tailored_resume_service,
        "generate_tailored_resume",
        MagicMock(return_value=generated),
    )
    monkeypatch.setattr(
        tailored_resume_service,
        "validate_tailored_resume_grounding",
        MagicMock(),
    )

    with pytest.raises(
        Exception,
        match="Database error",
    ):
        (
            tailored_resume_service
            .create_tailored_resume_for_user(
                analysis_id=12,
                source_content=source,
                current_user=user,
                db=db,
            )
        )

    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


def test_get_user_tailored_resumes_filters_by_user():
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    query = db.query.return_value
    filtered = query.filter.return_value
    ordered = filtered.order_by.return_value
    ordered.all.return_value = expected

    result = (
        tailored_resume_service
        .get_user_tailored_resumes(
            user_id=7,
            db=db,
        )
    )

    assert result == expected
    db.query.assert_called_once()


def test_get_user_tailored_resume_filters_by_id_and_user():
    db = MagicMock()
    expected = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        expected
    )

    result = (
        tailored_resume_service
        .get_user_tailored_resume(
            tailored_resume_id=12,
            user_id=7,
            db=db,
        )
    )

    assert result is expected
    db.query.assert_called_once()