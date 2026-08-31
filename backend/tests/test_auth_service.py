from datetime import datetime, timedelta, timezone

from jose import jwt

from app.services import auth_service


TEST_SECRET_KEY = "test-secret-key"


def test_hash_password_does_not_return_plain_password():
    password = "StrongPassword123"

    hashed_password = auth_service.hash_password(
        password
    )

    assert hashed_password != password


def test_verify_password_returns_true_for_correct_password():
    password = "StrongPassword123"

    hashed_password = auth_service.hash_password(
        password
    )

    assert auth_service.verify_password(
        password,
        hashed_password,
    ) is True


def test_verify_password_returns_false_for_wrong_password():
    hashed_password = auth_service.hash_password(
        "CorrectPassword123"
    )

    assert auth_service.verify_password(
        "WrongPassword123",
        hashed_password,
    ) is False


def test_create_and_verify_access_token(
    monkeypatch,
):
    monkeypatch.setattr(
        auth_service.settings,
        "SECRET_KEY",
        TEST_SECRET_KEY,
    )

    token = auth_service.create_access_token(
        {
            "sub": "user@example.com"
        }
    )

    email = auth_service.verify_token(
        token
    )

    assert email == "user@example.com"


def test_verify_token_returns_none_when_sub_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        auth_service.settings,
        "SECRET_KEY",
        TEST_SECRET_KEY,
    )

    token = auth_service.create_access_token(
        {
            "user_id": 1
        }
    )

    result = auth_service.verify_token(
        token
    )

    assert result is None


def test_verify_token_returns_none_for_invalid_token(
    monkeypatch,
):
    monkeypatch.setattr(
        auth_service.settings,
        "SECRET_KEY",
        TEST_SECRET_KEY,
    )

    result = auth_service.verify_token(
        "this-is-not-a-valid-token"
    )

    assert result is None


def test_verify_token_returns_none_for_expired_token(
    monkeypatch,
):
    monkeypatch.setattr(
        auth_service.settings,
        "SECRET_KEY",
        TEST_SECRET_KEY,
    )

    expired_payload = {
        "sub": "user@example.com",
        "exp": (
            datetime.now(timezone.utc)
            - timedelta(minutes=5)
        ),
    }

    token = jwt.encode(
        expired_payload,
        TEST_SECRET_KEY,
        algorithm=auth_service.settings.JWT_ALGORITHM,
    )

    result = auth_service.verify_token(
        token
    )

    assert result is None