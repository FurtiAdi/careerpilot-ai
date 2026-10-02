from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models.cover_letter_schema import (
    CoverLetterAIResponse,
    CoverLetterContent,
)
from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services import cover_letter_service


def make_source_resume() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={"full_name": "Ada Lovelace"},
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
                "bullets": ["Built Python applications."],
            }
        ],
        skills=["Python"],
    )


def make_generated_letter() -> CoverLetterAIResponse:
    return CoverLetterAIResponse(
        content={
            "opening": "I am applying for the Python role.",
            "evidence": ["Built Python applications."],
            "motivation": "The role aligns with my experience.",
            "closing": "Thank you for your consideration.",
        }
    )


def test_create_cover_letter_persists_grounded_result(
    monkeypatch,
):
    db = MagicMock()
    user = SimpleNamespace(id=7)
    analysis = SimpleNamespace(
        id=12,
        user_id=7,
        job_description="Python engineer role",
        candidate_skills="Python",
    )
    saved_resume = SimpleNamespace(
        id=21,
        storage_filename="saved-resume.pdf",
    )

    db.query.return_value.filter.return_value.first.return_value = (
        analysis
    )

    source = make_source_resume()
    generated = make_generated_letter()
    snapshot = {
        "match_score": 80,
        "missing_required_skills": [],
        "missing_preferred_skills": [],
    }

    monkeypatch.setattr(
        cover_letter_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "build_grounded_saved_resume_content_from_record",
        MagicMock(return_value=source),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "build_analysis_match_snapshot",
        MagicMock(return_value=snapshot),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "generate_cover_letter",
        MagicMock(return_value=generated),
    )
    mock_validate = MagicMock()
    monkeypatch.setattr(
        cover_letter_service,
        "validate_cover_letter_grounding",
        mock_validate,
    )

    result = cover_letter_service.create_cover_letter_for_user(
        analysis_id=12,
        source_resume_id=21,
        source_tailored_resume_id=None,
        tone="professional",
        length="standard",
        current_user=user,
        db=db,
    )

    assert result.user_id == 7
    assert result.source_analysis_id == 12
    assert result.source_resume_id == 21
    assert result.source_tailored_resume_id is None
    assert result.status == "draft"
    assert result.content == generated.content.model_dump(
        mode="json"
    )

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    mock_validate.assert_called_once_with(
        source_resume=source,
        generated=generated.content,
        match_snapshot=snapshot,
    )


def test_cover_letter_grounding_rejects_missing_skill_claim():
    source = make_source_resume()
    generated = CoverLetterContent(
        opening="I have Docker experience.",
        evidence=[],
        motivation="I am interested in the role.",
        closing="Thank you.",
    )

    with pytest.raises(
        cover_letter_service.CoverLetterGroundingError,
        match="missing skill",
    ):
        cover_letter_service.validate_cover_letter_grounding(
            source_resume=source,
            generated=generated,
            match_snapshot={
                "missing_required_skills": ["docker"],
            },
        )


def test_cover_letter_grounding_rejects_invented_quantity():
    source = make_source_resume()
    generated = CoverLetterContent(
        opening="I improved performance by 50%.",
        evidence=[],
        motivation="I am interested in the role.",
        closing="Thank you.",
    )

    with pytest.raises(
        cover_letter_service.CoverLetterGroundingError,
        match="unsupported quantity",
    ):
        cover_letter_service.validate_cover_letter_grounding(
            source_resume=source,
            generated=generated,
            match_snapshot={},
        )

def test_get_user_cover_letters_filters_by_user():
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    query = db.query.return_value
    filtered = query.filter.return_value
    ordered = filtered.order_by.return_value
    ordered.all.return_value = expected

    result = cover_letter_service.get_user_cover_letters(
        user_id=7,
        db=db,
    )

    assert result == expected
    db.query.assert_called_once()


def test_get_user_cover_letter_filters_by_id_and_user():
    db = MagicMock()
    expected = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        expected
    )

    result = cover_letter_service.get_user_cover_letter(
        cover_letter_id=12,
        user_id=7,
        db=db,
    )

    assert result is expected
    db.query.assert_called_once()

def make_persisted_cover_letter():
    return SimpleNamespace(
        id=12,
        user_id=7,
        source_analysis_id=20,
        source_resume_id=21,
        source_tailored_resume_id=None,
        version_group_id="group-id",
        version_number=2,
        status="draft",
        tone="professional",
        length="standard",
        content=make_generated_letter().content.model_dump(
            mode="json"
        ),
    )


def test_update_creates_new_cover_letter_version(
    monkeypatch,
):
    db = MagicMock()
    existing = make_persisted_cover_letter()

    monkeypatch.setattr(
        cover_letter_service,
        "get_user_cover_letter",
        MagicMock(return_value=existing),
    )
    db.query.return_value.filter.return_value.scalar.return_value = (
        3
    )

    updated_content = CoverLetterContent(
        opening="Updated opening.",
        evidence=["Built Python applications."],
        motivation="Updated motivation.",
        closing="Updated closing.",
    )

    result = (
        cover_letter_service
        .create_user_cover_letter_version(
            cover_letter_id=12,
            user_id=7,
            content=updated_content,
            status="saved",
            db=db,
        )
    )

    assert result.user_id == 7
    assert result.version_group_id == "group-id"
    assert result.version_number == 4
    assert result.status == "saved"
    assert result.content["opening"] == "Updated opening."

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_update_cover_letter_returns_none_when_not_owned(
    monkeypatch,
):
    db = MagicMock()

    monkeypatch.setattr(
        cover_letter_service,
        "get_user_cover_letter",
        MagicMock(return_value=None),
    )

    result = (
        cover_letter_service
        .create_user_cover_letter_version(
            cover_letter_id=99,
            user_id=7,
            content=None,
            status="saved",
            db=db,
        )
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_delete_user_cover_letter_is_scoped_to_user(
    monkeypatch,
):
    db = MagicMock()
    existing = make_persisted_cover_letter()

    monkeypatch.setattr(
        cover_letter_service,
        "get_user_cover_letter",
        MagicMock(return_value=existing),
    )

    result = cover_letter_service.delete_user_cover_letter(
        cover_letter_id=12,
        user_id=7,
        db=db,
    )

    assert result is existing
    db.delete.assert_called_once_with(existing)
    db.commit.assert_called_once()

def test_regenerate_creates_new_cover_letter_version(
    monkeypatch,
):
    db = MagicMock()
    existing = make_persisted_cover_letter()
    analysis = SimpleNamespace(
        id=20,
        user_id=7,
        job_description="Python engineer role",
        candidate_skills="Python",
    )
    saved_resume = SimpleNamespace(
        id=21,
        storage_filename="saved-resume.pdf",
    )
    source = make_source_resume()
    generated = make_generated_letter()
    snapshot = {
        "match_score": 80,
        "missing_required_skills": [],
        "missing_preferred_skills": [],
    }

    analysis_query = MagicMock()
    analysis_query.filter.return_value.first.return_value = (
        analysis
    )
    version_query = MagicMock()
    version_query.filter.return_value.scalar.return_value = 3
    db.query.side_effect = [analysis_query, version_query]

    monkeypatch.setattr(
        cover_letter_service,
        "get_user_cover_letter",
        MagicMock(return_value=existing),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "build_grounded_saved_resume_content_from_record",
        MagicMock(return_value=source),
    )
    monkeypatch.setattr(
        cover_letter_service,
        "build_analysis_match_snapshot",
        MagicMock(return_value=snapshot),
    )
    mock_generate = MagicMock(return_value=generated)
    monkeypatch.setattr(
        cover_letter_service,
        "generate_cover_letter",
        mock_generate,
    )
    mock_validate = MagicMock()
    monkeypatch.setattr(
        cover_letter_service,
        "validate_cover_letter_grounding",
        mock_validate,
    )

    result = (
        cover_letter_service
        .regenerate_user_cover_letter(
            cover_letter_id=12,
            user_id=7,
            db=db,
        )
    )

    assert result.user_id == 7
    assert result.source_analysis_id == 20
    assert result.source_resume_id == 21
    assert result.version_group_id == "group-id"
    assert result.version_number == 4
    assert result.status == "draft"
    assert result.tone == "professional"
    assert result.length == "standard"
    assert result.content == generated.content.model_dump(
        mode="json"
    )

    mock_generate.assert_called_once_with(
        resume_content=source,
        job_description="Python engineer role",
        match_snapshot=snapshot,
        tone="professional",
        length="standard",
    )
    mock_validate.assert_called_once_with(
        source_resume=source,
        generated=generated.content,
        match_snapshot=snapshot,
    )
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)