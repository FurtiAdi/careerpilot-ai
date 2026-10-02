from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.cover_letter_schema import (
    CoverLetterGenerateRequest,
    CoverLetterResponse,
    CoverLetterUpdateRequest,
)


def make_content() -> dict:
    return {
        "opening": "I am applying for the Software Engineer role.",
        "evidence": [
            "Built Python applications.",
        ],
        "motivation": "The role aligns with my backend experience.",
        "closing": "Thank you for your consideration.",
    }


def test_generate_request_accepts_conservative_defaults():
    request = CoverLetterGenerateRequest(
        analysis_id=12,
        source_resume_id=21,
    )

    assert request.tone == "professional"
    assert request.length == "standard"


def test_generate_request_rejects_invalid_source_resume_id():
    with pytest.raises(ValidationError):
        CoverLetterGenerateRequest(
            analysis_id=12,
            source_resume_id=0,
        )


def test_generate_request_rejects_client_supplied_content():
    with pytest.raises(ValidationError):
        CoverLetterGenerateRequest(
            analysis_id=12,
            source_resume_id=21,
            content=make_content(),
        )


def test_cover_letter_response_serializes_orm_record():
    now = datetime.now(timezone.utc)

    record = SimpleNamespace(
        id=4,
        user_id=7,
        source_analysis_id=12,
        source_resume_id=21,
        source_tailored_resume_id=None,
        version_group_id="version-group",
        version_number=1,
        status="draft",
        tone="professional",
        length="standard",
        content=make_content(),
        created_at=now,
        updated_at=now,
    )

    response = CoverLetterResponse.model_validate(record)

    assert response.id == 4
    assert response.content.evidence == [
        "Built Python applications."
    ]


def test_update_request_requires_at_least_one_change():
    with pytest.raises(
        ValidationError,
        match="At least one field",
    ):
        CoverLetterUpdateRequest()