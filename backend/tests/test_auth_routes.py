from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.user_schema import UserLogin
from app.routes import auth_routes


@pytest.mark.anyio
async def test_register_user_success_returns_access_token(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_user = SimpleNamespace(
        email="test@example.com",
    )

    monkeypatch.setattr(
        auth_routes,
        "register_user",
        MagicMock(return_value=mock_user),
    )

    mock_create_access_token = MagicMock(
        return_value="new-user-access-token",
    )
    monkeypatch.setattr(
        auth_routes,
        "create_access_token",
        mock_create_access_token,
    )

    result = await auth_routes.register_user_route(
        full_name="Test User",
        email="test@example.com",
        password="password123",
        resume=None,
        profile_picture=None,
        db=mock_db,
    )

    assert result == {
        "access_token": "new-user-access-token",
        "token_type": "bearer",
    }
    mock_create_access_token.assert_called_once_with(
        data={
            "sub": "test@example.com",
        }
    )


@pytest.mark.anyio
async def test_register_user_duplicate_email_returns_409(
    monkeypatch,
):
    mock_db = MagicMock()

    monkeypatch.setattr(
        auth_routes,
        "register_user",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await auth_routes.register_user_route(
            full_name="Test User",
            email="test@example.com",
            password="password123",
            resume=None,
            profile_picture=None,
            db=mock_db,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Email already exists"


def test_login_success(monkeypatch):
    mock_db = MagicMock()

    monkeypatch.setattr(
        auth_routes,
        "authenticate_user",
        MagicMock(
            return_value="test-access-token"
        ),
    )

    login_data = UserLogin(
        email="test@example.com",
        password="password123",
    )

    result = auth_routes.login_user(
        user=login_data,
        db=mock_db,
    )

    assert result == {
        "access_token": "test-access-token",
        "token_type": "bearer",
    }


def test_login_invalid_credentials_returns_401(
    monkeypatch,
):
    mock_db = MagicMock()

    monkeypatch.setattr(
        auth_routes,
        "authenticate_user",
        MagicMock(return_value=None),
    )

    login_data = UserLogin(
        email="test@example.com",
        password="wrong-password",
    )

    with pytest.raises(HTTPException) as exc:
        auth_routes.login_user(
            user=login_data,
            db=mock_db,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == (
        "Invalid email or password"
    )