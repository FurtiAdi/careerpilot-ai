from pathlib import Path

from fastapi.testclient import TestClient

from app.dependencies.auth_dependencies import (
    get_current_user,
)
from app.main import app
from app.models.user_model import User


client = TestClient(app)


def make_user(
    resume_filename=None,
    profile_picture_filename=None,
):
    user = User(
        id=1,
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed",
        resume_filename=resume_filename,
        profile_picture_filename=(
            profile_picture_filename
        ),
    )

    return user


def test_get_profile_requires_authentication():
    response = client.get("/me")

    assert response.status_code == 401


def test_get_current_user_profile():
    user = make_user()

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    try:
        response = client.get("/me")

        assert response.status_code == 200

        assert response.json() == {
            "id": 1,
            "full_name": "Test User",
            "email": "test@example.com",
            "resume_filename": None,
            "profile_picture_filename": None,
        }

    finally:
        app.dependency_overrides.clear()


def test_profile_picture_returns_404_when_missing():
    user = make_user(
        profile_picture_filename=None
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    try:
        response = client.get(
            "/profile-picture"
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Profile picture not found."
        }

    finally:
        app.dependency_overrides.clear()


def test_resume_returns_404_when_missing():
    user = make_user(
        resume_filename=None
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    try:
        response = client.get("/resume")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Resume not found."
        }

    finally:
        app.dependency_overrides.clear()


def test_profile_picture_file_is_returned(
    tmp_path,
    monkeypatch,
):
    upload_dir = (
        tmp_path
        / "uploads"
        / "profile_pictures"
    )

    upload_dir.mkdir(
        parents=True
    )

    image_path = upload_dir / "profile.png"

    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\nfake-image"
    )

    user = make_user(
        profile_picture_filename="profile.png"
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    monkeypatch.chdir(tmp_path)

    try:
        response = client.get(
            "/profile-picture"
        )

        assert response.status_code == 200
        assert response.content == (
            b"\x89PNG\r\n\x1a\nfake-image"
        )

    finally:
        app.dependency_overrides.clear()


def test_resume_file_is_returned(
    tmp_path,
    monkeypatch,
):
    upload_dir = (
        tmp_path
        / "uploads"
        / "resumes"
    )

    upload_dir.mkdir(
        parents=True
    )

    resume_path = upload_dir / "resume.pdf"

    resume_path.write_bytes(
        b"%PDF-1.4 fake resume"
    )

    user = make_user(
        resume_filename="resume.pdf"
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    monkeypatch.chdir(tmp_path)

    try:
        response = client.get("/resume")

        assert response.status_code == 200
        assert response.headers[
            "content-type"
        ].startswith(
            "application/pdf"
        )

    finally:
        app.dependency_overrides.clear()

def test_profile_stats_returns_user_stats(
    monkeypatch,
):
    user = make_user(
        resume_filename="resume.pdf"
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    expected = {
        "total_analyses": 3,
        "average_match_score": 75,
        "resume_uploaded": True,
    }

    from app.routes import profile_routes

    monkeypatch.setattr(
        profile_routes,
        "get_profile_stats",
        lambda current_user, db: expected,
    )

    try:
        response = client.get(
            "/profile-stats"
        )

        assert response.status_code == 200
        assert response.json() == expected

    finally:
        app.dependency_overrides.clear()


def test_profile_stats_requires_authentication():
    response = client.get(
        "/profile-stats"
    )

    assert response.status_code == 401