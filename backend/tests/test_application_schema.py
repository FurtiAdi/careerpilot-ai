from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.application_schema import (
    ApplicationCreateRequest,
    ApplicationEventResponse,
    ApplicationResponse,
    ApplicationUpdateRequest,
)


def test_create_request_accepts_valid_application():
    request = ApplicationCreateRequest(
        company="Example Corp",
        role="Backend Engineer",
        job_url="https://example.com/jobs/123",
        job_description="Build Python services.",
        applied_at=date(2026, 10, 2),
        next_action_date=date(2026, 10, 9),
        notes="Follow up with the recruiter.",
        analysis_id=12,
        tailored_resume_id=21,
        cover_letter_id=34,
    )

    assert request.status == "saved"
    assert request.company == "Example Corp"
    assert request.analysis_id == 12
    assert request.cover_letter_id == 34


def test_create_request_rejects_invalid_status():
    with pytest.raises(ValidationError):
        ApplicationCreateRequest(
            company="Example Corp",
            role="Backend Engineer",
            status="hired",
        )


def test_create_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ApplicationCreateRequest(
            company="Example Corp",
            role="Backend Engineer",
            user_id=99,
        )


def test_update_request_requires_at_least_one_change():
    with pytest.raises(
        ValidationError,
        match="At least one field",
    ):
        ApplicationUpdateRequest()


def test_application_response_serializes_orm_record():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=4,
        user_id=7,
        company="Example Corp",
        role="Backend Engineer",
        status="applied",
        job_url="https://example.com/jobs/123",
        job_description="Build Python services.",
        applied_at=date(2026, 10, 2),
        next_action_date=date(2026, 10, 9),
        notes="Follow up with the recruiter.",
        analysis_id=12,
        tailored_resume_id=21,
        cover_letter_id=34,
        created_at=now,
        updated_at=now,
    )

    response = ApplicationResponse.model_validate(record)

    assert response.id == 4
    assert response.status == "applied"
    assert response.next_action_date == date(2026, 10, 9)


def test_application_event_response_serializes_orm_record():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=8,
        application_id=4,
        user_id=7,
        event_type="status_changed",
        previous_status="saved",
        new_status="applied",
        note="Application submitted.",
        created_at=now,
    )

    response = ApplicationEventResponse.model_validate(record)

    assert response.application_id == 4
    assert response.previous_status == "saved"
    assert response.new_status == "applied"