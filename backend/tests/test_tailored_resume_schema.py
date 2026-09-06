import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from types import SimpleNamespace

from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
    TailoredResumeGenerateRequest,
    TailoredResumeResponse,
    TailoredResumeUpdateRequest,
)


def test_tailored_resume_response_accepts_structured_content():
    response = TailoredResumeAIResponse(
        content={
            "contact": {
                "full_name": "Ada Lovelace",
                "email": "ada@example.com",
            },
            "summary": "Software engineer.",
            "experience": [
                {
                    "employer": "Example Company",
                    "title": "Software Engineer",
                    "bullets": [
                        "Built Python applications."
                    ],
                }
            ],
            "skills": ["Python"],
        },
        emphasized_items=["Python experience"],
        reordered_items=[],
    )

    assert response.content.contact.full_name == "Ada Lovelace"
    assert response.content.skills == ["Python"]
    assert response.emphasized_items == [
        "Python experience"
    ]


def test_tailored_resume_response_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        TailoredResumeAIResponse(
            content={
                "contact": {},
                "invented_section": [
                    "Unsupported content"
                ],
            }
        )


def test_generate_request_rejects_invalid_analysis_id():
    with pytest.raises(ValidationError):
        TailoredResumeGenerateRequest(
            analysis_id=0
        )


def test_generate_request_rejects_client_source_content():
    with pytest.raises(ValidationError):
        TailoredResumeGenerateRequest(
            analysis_id=12,
            source_content={
                "contact": {
                    "full_name": "Unverified User"
                }
            },
        )


def test_tailored_resume_response_serializes_orm_record():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=4,
        user_id=7,
        source_analysis_id=12,
        source_resume_filename="saved-resume.pdf",
        version_group_id="version-group",
        version_number=1,
        status="draft",
        content={
            "contact": {
                "full_name": "Ada Lovelace",
            },
            "skills": ["Python"],
        },
        emphasized_items=["Python"],
        reordered_items=["Experience"],
        match_snapshot={
            "match_score": 80,
            "missing_required_skills": ["docker"],
        },
        created_at=now,
        updated_at=now,
    )

    response = TailoredResumeResponse.model_validate(
        record
    )

    assert response.id == 4
    assert response.user_id == 7
    assert response.content.skills == ["Python"]
    assert response.status == "draft"


def test_update_request_requires_at_least_one_change():
    with pytest.raises(
        ValidationError,
        match="At least one field",
    ):
        TailoredResumeUpdateRequest()