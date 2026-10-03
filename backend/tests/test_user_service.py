import pytest

from unittest.mock import MagicMock

from app.models.saved_resume_model import SavedResume
from app.models.user_model import User
from app.services import user_service

def test_register_user_creates_account_without_uploads(
    monkeypatch,
):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (
        None
    )

    monkeypatch.setattr(
        user_service,
        "hash_password",
        MagicMock(return_value="hashed-password"),
    )

    result = user_service.register_user(
        full_name="Ada Lovelace",
        email="ada@example.com",
        password="secure-password",
        resume_content=None,
        resume_original_filename=None,
        profile_picture_content=None,
        profile_picture_content_type=None,
        db=db,
    )

    assert isinstance(result, User)
    assert result.full_name == "Ada Lovelace"
    assert result.email == "ada@example.com"
    assert result.resume_filename is None
    assert result.profile_picture_filename is None

    db.add.assert_called_once_with(result)
    db.flush.assert_called_once()
    db.commit.assert_called_once()

def test_register_user_creates_saved_resume_for_uploaded_pdf(
    tmp_path,
    monkeypatch,
):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (
        None
    )

    monkeypatch.setattr(
        user_service.settings,
        "RESUME_DIR",
        str(tmp_path),
    )
    monkeypatch.setattr(
        user_service,
        "hash_password",
        MagicMock(return_value="hashed-password"),
    )
    monkeypatch.setattr(
        user_service,
        "generate_resume_filename",
        MagicMock(return_value="new-resume.pdf"),
    )

    def assign_user_id():
        new_user = db.add.call_args_list[0].args[0]
        new_user.id = 7

    db.flush.side_effect = assign_user_id

    result = user_service.register_user(
        full_name="Ada Lovelace",
        email="ada@example.com",
        password="secure-password",
        resume_content=b"%PDF-1.4 test",
        resume_original_filename="Ada Resume.pdf",
        profile_picture_content=None,
        profile_picture_content_type=None,
        db=db,
    )

    assert isinstance(result, User)
    assert result.resume_filename == "new-resume.pdf"

    saved_resume = db.add.call_args_list[1].args[0]
    assert isinstance(saved_resume, SavedResume)
    assert saved_resume.user_id == 7
    assert saved_resume.storage_filename == "new-resume.pdf"
    assert saved_resume.original_filename == "Ada Resume.pdf"

    assert (tmp_path / "new-resume.pdf").is_file()
    db.flush.assert_called_once()
    db.commit.assert_called_once()


def test_register_user_removes_resume_file_when_flush_fails(
    tmp_path,
    monkeypatch,
):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (
        None
    )
    db.flush.side_effect = Exception("Database error")

    monkeypatch.setattr(
        user_service.settings,
        "RESUME_DIR",
        str(tmp_path),
    )
    monkeypatch.setattr(
        user_service,
        "hash_password",
        MagicMock(return_value="hashed-password"),
    )
    monkeypatch.setattr(
        user_service,
        "generate_resume_filename",
        MagicMock(return_value="new-resume.pdf"),
    )

    with pytest.raises(Exception, match="Database error"):
        user_service.register_user(
            full_name="Ada Lovelace",
            email="ada@example.com",
            password="secure-password",
            resume_content=b"%PDF-1.4 test",
            resume_original_filename="Ada Resume.pdf",
            profile_picture_content=None,
            profile_picture_content_type=None,
            db=db,
        )

    assert not (tmp_path / "new-resume.pdf").exists()
    db.rollback.assert_called_once()
    db.commit.assert_not_called()