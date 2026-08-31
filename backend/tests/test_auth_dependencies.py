from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.dependencies import auth_dependencies


def test_missing_token_returns_401():
    mock_db = MagicMock()

    with pytest.raises(HTTPException) as exc:
        auth_dependencies.get_current_user(
            token=None,
            db=mock_db,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == (
        "Authentication token is required."
    )


def test_invalid_token_returns_401(
    monkeypatch,
):
    mock_db = MagicMock()

    monkeypatch.setattr(
        auth_dependencies,
        "verify_token",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        auth_dependencies.get_current_user(
            token="invalid-token",
            db=mock_db,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == (
        "Invalid or expired authentication token."
    )


def test_valid_token_without_user_returns_401(
    monkeypatch,
):
    mock_db = MagicMock()

    monkeypatch.setattr(
        auth_dependencies,
        "verify_token",
        MagicMock(
            return_value="user@example.com"
        ),
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_dependencies.get_current_user(
            token="valid-token",
            db=mock_db,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == (
        "Invalid or expired authentication token."
    )


def test_valid_token_returns_user(
    monkeypatch,
):
    mock_db = MagicMock()
    mock_user = MagicMock()

    monkeypatch.setattr(
        auth_dependencies,
        "verify_token",
        MagicMock(
            return_value="user@example.com"
        ),
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_user

    result = auth_dependencies.get_current_user(
        token="valid-token",
        db=mock_db,
    )

    assert result == mock_user