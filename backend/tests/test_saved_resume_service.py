from unittest.mock import MagicMock

import pytest

from app.services import saved_resume_service


def test_create_saved_resume_writes_file_and_persists_record(
    tmp_path,
    monkeypatch,
):
    resume_directory = tmp_path / "resumes"
    db = MagicMock()

    monkeypatch.setattr(
        saved_resume_service.settings,
        "RESUME_DIR",
        str(resume_directory),
    )
    monkeypatch.setattr(
        saved_resume_service,
        "generate_resume_filename",
        lambda: "generated-resume.pdf",
    )

    saved_resume = (
        saved_resume_service.create_saved_resume(
            user_id=7,
            original_filename="my-resume.pdf",
            content=b"%PDF-1.4 test resume",
            db=db,
        )
    )

    assert saved_resume.user_id == 7
    assert saved_resume.storage_filename == (
        "generated-resume.pdf"
    )
    assert saved_resume.original_filename == "my-resume.pdf"
    assert (
        resume_directory / "generated-resume.pdf"
    ).read_bytes() == b"%PDF-1.4 test resume"
    db.add.assert_called_once_with(saved_resume)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(saved_resume)


def test_create_saved_resume_removes_file_when_commit_fails(
    tmp_path,
    monkeypatch,
):
    resume_directory = tmp_path / "resumes"
    db = MagicMock()
    db.commit.side_effect = RuntimeError("database unavailable")

    monkeypatch.setattr(
        saved_resume_service.settings,
        "RESUME_DIR",
        str(resume_directory),
    )
    monkeypatch.setattr(
        saved_resume_service,
        "generate_resume_filename",
        lambda: "generated-resume.pdf",
    )

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        saved_resume_service.create_saved_resume(
            user_id=7,
            original_filename="my-resume.pdf",
            content=b"%PDF-1.4 test resume",
            db=db,
        )

    assert not (
        resume_directory / "generated-resume.pdf"
    ).exists()
    db.rollback.assert_called_once()

def test_get_user_saved_resumes_filters_by_user():
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = expected

    result = (
        saved_resume_service.get_user_saved_resumes(
            user_id=7,
            db=db,
        )
    )

    assert result == expected
    db.query.assert_called_once_with(
        saved_resume_service.SavedResume
    )
    db.query.return_value.filter.assert_called_once()
    (
        db.query.return_value
        .filter.return_value
        .order_by
        .assert_called_once()
    )


def test_get_user_saved_resume_filters_by_id_and_user():
    db = MagicMock()
    expected = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = expected

    result = saved_resume_service.get_user_saved_resume(
        saved_resume_id=12,
        user_id=7,
        db=db,
    )

    assert result is expected
    db.query.assert_called_once_with(
        saved_resume_service.SavedResume
    )
    db.query.return_value.filter.assert_called_once()