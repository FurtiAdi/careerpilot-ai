from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.application_schema import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)

from app.services import application_service


def test_create_application_persists_initial_status_event():
    db = MagicMock()

    def assign_application_id():
        application = db.add.call_args_list[0].args[0]
        application.id = 4

    db.flush.side_effect = assign_application_id

    request = ApplicationCreateRequest(
        company="Example Corp",
        role="Backend Engineer",
        analysis_id=12,
        tailored_resume_id=21,
        cover_letter_id=34,
    )

    application = (
        application_service.create_application_for_user(
            request=request,
            user_id=7,
            db=db,
        )
    )

    created_application = db.add.call_args_list[0].args[0]
    initial_event = db.add.call_args_list[1].args[0]

    assert application is created_application
    assert application.id == 4
    assert application.user_id == 7
    assert application.company == "Example Corp"
    assert application.role == "Backend Engineer"
    assert application.status == "saved"
    assert application.analysis_id == 12
    assert application.tailored_resume_id == 21
    assert application.cover_letter_id == 34

    assert initial_event.application_id == 4
    assert initial_event.user_id == 7
    assert initial_event.event_type == "status_changed"
    assert initial_event.previous_status is None
    assert initial_event.new_status == "saved"

    assert db.add.call_count == 2
    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(application)


def test_get_user_applications_filters_by_user():
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = expected

    result = application_service.get_user_applications(
        user_id=7,
        db=db,
    )

    assert result == expected
    db.query.assert_called_once_with(
        application_service.Application
    )


def test_get_user_application_filters_by_id_and_user():
    db = MagicMock()
    expected = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = expected

    result = application_service.get_user_application(
        application_id=12,
        user_id=7,
        db=db,
    )

    assert result is expected
    db.query.assert_called_once_with(
        application_service.Application
    )

def test_update_application_status_creates_event(
    monkeypatch,
):
    db = MagicMock()
    existing = SimpleNamespace(
        id=4,
        user_id=7,
        company="Example Corp",
        role="Backend Engineer",
        status="saved",
        job_url=None,
        job_description=None,
        applied_at=None,
        next_action_date=None,
        notes=None,
        analysis_id=None,
        tailored_resume_id=None,
        cover_letter_id=None,
    )

    monkeypatch.setattr(
        application_service,
        "get_user_application",
        MagicMock(return_value=existing),
    )

    request = ApplicationUpdateRequest(
        status="applied",
        notes="Application submitted.",
    )

    result = application_service.update_user_application(
        application_id=4,
        request=request,
        user_id=7,
        db=db,
    )

    status_event = db.add.call_args.args[0]

    assert result is existing
    assert result.status == "applied"
    assert result.notes == "Application submitted."

    assert status_event.application_id == 4
    assert status_event.user_id == 7
    assert status_event.event_type == "status_changed"
    assert status_event.previous_status == "saved"
    assert status_event.new_status == "applied"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing)


def test_update_application_returns_none_when_not_owned(
    monkeypatch,
):
    db = MagicMock()

    monkeypatch.setattr(
        application_service,
        "get_user_application",
        MagicMock(return_value=None),
    )

    result = application_service.update_user_application(
        application_id=99,
        request=ApplicationUpdateRequest(
            notes="Should not be saved."
        ),
        user_id=7,
        db=db,
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_get_user_application_events_filters_by_application_and_user():
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = expected

    result = application_service.get_user_application_events(
        application_id=4,
        user_id=7,
        db=db,
    )

    assert result == expected
    db.query.assert_called_once_with(
        application_service.ApplicationEvent
    )


def test_delete_user_application_is_scoped_to_user(
    monkeypatch,
):
    db = MagicMock()
    existing = SimpleNamespace(
        id=4,
        user_id=7,
    )

    monkeypatch.setattr(
        application_service,
        "get_user_application",
        MagicMock(return_value=existing),
    )

    result = application_service.delete_user_application(
        application_id=4,
        user_id=7,
        db=db,
    )

    assert result is existing

    db.query.assert_called_once_with(
        application_service.ApplicationEvent
    )
    (
        db.query.return_value
        .filter.return_value
        .delete
        .assert_called_once_with(
            synchronize_session=False
        )
    )

    db.delete.assert_called_once_with(existing)
    db.commit.assert_called_once()


def test_delete_user_application_returns_none_when_not_owned(
    monkeypatch,
):
    db = MagicMock()

    monkeypatch.setattr(
        application_service,
        "get_user_application",
        MagicMock(return_value=None),
    )

    result = application_service.delete_user_application(
        application_id=99,
        user_id=7,
        db=db,
    )

    assert result is None
    db.delete.assert_not_called()
    db.commit.assert_not_called()