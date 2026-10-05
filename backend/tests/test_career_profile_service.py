from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models.career_profile_schema import (
    CareerProfileContent,
)
from app.services import career_profile_service
from app.services.resume_service import (
    SavedResumeNotFoundError,
)


def make_profile_content() -> CareerProfileContent:
    return CareerProfileContent(
        contact={
            "full_name": "Ada Lovelace",
        },
        experience=[
            {
                "title": "Software Engineer",
                "employer": "Real Company",
            }
        ],
        skills=["Python"],
    )


def test_extract_and_persist_creates_draft_profile(
    monkeypatch,
):
    db = MagicMock()
    saved_resume = SimpleNamespace(id=21)

    monkeypatch.setattr(
        career_profile_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        career_profile_service,
        "get_user_career_profile",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        career_profile_service,
        "build_grounded_career_profile_content_from_record",
        MagicMock(return_value=make_profile_content()),
    )

    result = (
        career_profile_service
        .extract_and_persist_career_profile_for_user(
            source_resume_id=21,
            user_id=7,
            db=db,
        )
    )

    assert result.user_id == 7
    assert result.source_resume_id == 21
    assert result.status == "draft"
    assert result.content == make_profile_content().model_dump(
        mode="json"
    )

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_extract_and_persist_refreshes_existing_draft(
    monkeypatch,
):
    db = MagicMock()
    saved_resume = SimpleNamespace(id=25)
    existing_profile = SimpleNamespace(
        id=4,
        user_id=7,
        source_resume_id=21,
        status="draft",
        content={"skills": ["Old Skill"]},
    )
    content = make_profile_content()

    monkeypatch.setattr(
        career_profile_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        career_profile_service,
        "get_user_career_profile",
        MagicMock(return_value=existing_profile),
    )
    monkeypatch.setattr(
        career_profile_service,
        "build_grounded_career_profile_content_from_record",
        MagicMock(return_value=content),
    )

    result = (
        career_profile_service
        .extract_and_persist_career_profile_for_user(
            source_resume_id=25,
            user_id=7,
            db=db,
        )
    )

    assert result is existing_profile
    assert result.source_resume_id == 25
    assert result.status == "draft"
    assert result.content == content.model_dump(mode="json")

    db.add.assert_not_called()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing_profile)


def test_extract_and_persist_rejects_non_owned_resume(
    monkeypatch,
):
    db = MagicMock()
    mock_extract = MagicMock()

    monkeypatch.setattr(
        career_profile_service,
        "get_user_saved_resume",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        career_profile_service,
        "build_grounded_career_profile_content_from_record",
        mock_extract,
    )

    with pytest.raises(
        SavedResumeNotFoundError,
        match="selected source resume",
    ):
        (
            career_profile_service
            .extract_and_persist_career_profile_for_user(
                source_resume_id=21,
                user_id=7,
                db=db,
            )
        )

    mock_extract.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_extract_and_persist_rejects_reviewed_profile(
    monkeypatch,
):
    db = MagicMock()
    saved_resume = SimpleNamespace(id=21)
    reviewed_profile = SimpleNamespace(
        id=4,
        user_id=7,
        source_resume_id=21,
        status="reviewed",
    )
    mock_extract = MagicMock()

    monkeypatch.setattr(
        career_profile_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        career_profile_service,
        "get_user_career_profile",
        MagicMock(return_value=reviewed_profile),
    )
    monkeypatch.setattr(
        career_profile_service,
        "build_grounded_career_profile_content_from_record",
        mock_extract,
    )

    with pytest.raises(
        career_profile_service.CareerProfileReviewedError,
        match="cannot be overwritten",
    ):
        (
            career_profile_service
            .extract_and_persist_career_profile_for_user(
                source_resume_id=21,
                user_id=7,
                db=db,
            )
        )

    mock_extract.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_extract_and_persist_rolls_back_on_commit_error(
    monkeypatch,
):
    db = MagicMock()
    db.commit.side_effect = RuntimeError(
        "database unavailable"
    )
    saved_resume = SimpleNamespace(id=21)

    monkeypatch.setattr(
        career_profile_service,
        "get_user_saved_resume",
        MagicMock(return_value=saved_resume),
    )
    monkeypatch.setattr(
        career_profile_service,
        "get_user_career_profile",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        career_profile_service,
        "build_grounded_career_profile_content_from_record",
        MagicMock(return_value=make_profile_content()),
    )

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        (
            career_profile_service
            .extract_and_persist_career_profile_for_user(
                source_resume_id=21,
                user_id=7,
                db=db,
            )
        )

    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


def test_get_user_career_profile_filters_by_user():
    db = MagicMock()
    expected = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        expected
    )

    result = career_profile_service.get_user_career_profile(
        user_id=7,
        db=db,
    )

    assert result is expected
    db.query.assert_called_once_with(
        career_profile_service.CareerProfile
    )
    db.query.return_value.filter.assert_called_once()