from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.application_schema import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from app.routes import application_routes


client = TestClient(app)


def make_create_request() -> ApplicationCreateRequest:
    return ApplicationCreateRequest(
        company="Example Corp",
        role="Backend Engineer",
    )


def test_create_application_requires_authentication():
    response = client.post(
        "/applications",
        json={
            "company": "Example Corp",
            "role": "Backend Engineer",
        },
    )

    assert response.status_code == 401


def test_create_application_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    application = MagicMock()

    mock_service = MagicMock(return_value=application)
    monkeypatch.setattr(
        application_routes,
        "create_application_for_user",
        mock_service,
    )

    result = application_routes.create_application(
        request=make_create_request(),
        db=db,
        current_user=user,
    )

    assert result is application
    mock_service.assert_called_once_with(
        request=make_create_request(),
        user_id=7,
        db=db,
    )


def test_list_applications_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    applications = [MagicMock()]

    mock_service = MagicMock(return_value=applications)
    monkeypatch.setattr(
        application_routes,
        "get_user_applications",
        mock_service,
    )

    result = application_routes.list_applications(
        db=db,
        current_user=user,
    )

    assert result == applications
    mock_service.assert_called_once_with(
        user_id=7,
        db=db,
    )


def test_get_application_returns_404_when_not_owned(
    monkeypatch,
):
    monkeypatch.setattr(
        application_routes,
        "get_user_application",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        application_routes.get_application(
            application_id=99,
            db=MagicMock(),
            current_user=MagicMock(),
        )

    assert exc.value.status_code == 404


def test_update_application_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    updated_application = MagicMock()

    mock_service = MagicMock(return_value=updated_application)
    monkeypatch.setattr(
        application_routes,
        "update_user_application",
        mock_service,
    )

    request = ApplicationUpdateRequest(status="applied")

    result = application_routes.update_application(
        application_id=4,
        request=request,
        db=db,
        current_user=user,
    )

    assert result is updated_application
    mock_service.assert_called_once_with(
        application_id=4,
        request=request,
        user_id=7,
        db=db,
    )


def test_list_application_events_uses_current_user(
    monkeypatch,
):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    events = [MagicMock()]

    mock_service = MagicMock(return_value=events)
    monkeypatch.setattr(
        application_routes,
        "get_user_application_events",
        mock_service,
    )

    result = application_routes.list_application_events(
        application_id=4,
        db=db,
        current_user=user,
    )

    assert result == events
    mock_service.assert_called_once_with(
        application_id=4,
        user_id=7,
        db=db,
    )


def test_delete_application_uses_current_user(monkeypatch):
    db = MagicMock()
    user = MagicMock()
    user.id = 7
    deleted_application = MagicMock()

    mock_service = MagicMock(return_value=deleted_application)
    monkeypatch.setattr(
        application_routes,
        "delete_user_application",
        mock_service,
    )

    result = application_routes.delete_application(
        application_id=4,
        db=db,
        current_user=user,
    )

    assert result == {
        "message": "Application deleted."
    }
    mock_service.assert_called_once_with(
        application_id=4,
        user_id=7,
        db=db,
    )