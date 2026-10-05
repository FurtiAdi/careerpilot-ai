from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.career_profile_schema import (
    CareerProfileContent,
    CareerProfileExtractRequest,
    CareerProfileResponse,
)


def test_career_profile_content_accepts_structured_sections():
    content = CareerProfileContent(
        contact={
            "full_name": "Ada Lovelace",
            "headline": "Software Engineer",
            "email": "ada@example.com",
            "location": "Stockholm, Sweden",
            "links": ["https://example.com/ada"],
        },
        experience=[
            {
                "title": "Software Engineer",
                "employer": "Example Company",
                "start_date": "2024",
                "bullets": [
                    "Built Python applications.",
                ],
            }
        ],
        education=[
            {
                "institution": "Example University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
            }
        ],
        skills=["Python", "SQL"],
        certificates=[
            {
                "name": "Cloud Fundamentals",
                "issuer": "Example Provider",
                "date": "2025",
            }
        ],
    )

    assert content.contact.full_name == "Ada Lovelace"
    assert content.contact.headline == "Software Engineer"
    assert content.experience[0].employer == "Example Company"
    assert content.education[0].institution == "Example University"
    assert content.skills == ["Python", "SQL"]
    assert content.certificates[0].name == "Cloud Fundamentals"


def test_career_profile_content_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        CareerProfileContent(
            contact={},
            preferred_job_roles=["Backend Developer"],
        )


def test_career_profile_response_serializes_orm_record():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=4,
        user_id=7,
        source_resume_id=21,
        status="draft",
        content={
            "contact": {
                "full_name": "Ada Lovelace",
            },
            "experience": [],
            "education": [],
            "skills": ["Python"],
            "certificates": [],
        },
        created_at=now,
        updated_at=now,
    )

    response = CareerProfileResponse.model_validate(record)

    assert response.id == 4
    assert response.user_id == 7
    assert response.source_resume_id == 21
    assert response.status == "draft"
    assert response.content.skills == ["Python"]


def test_career_profile_response_rejects_unsupported_status():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=4,
        user_id=7,
        source_resume_id=21,
        status="saved",
        content={
            "contact": {},
        },
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(ValidationError):
        CareerProfileResponse.model_validate(record)


def test_career_profile_extract_request_rejects_invalid_resume_id():
    with pytest.raises(ValidationError):
        CareerProfileExtractRequest(
            source_resume_id=0,
        )