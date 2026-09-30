from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.saved_resume_schema import (
    SavedResumeResponse,
)


def test_saved_resume_response_exposes_safe_metadata():
    created_at = datetime.now(timezone.utc)

    response = SavedResumeResponse.model_validate(
        {
            "id": 4,
            "original_filename": "my-resume.pdf",
            "created_at": created_at,
        }
    )

    assert response.id == 4
    assert response.original_filename == "my-resume.pdf"
    assert response.created_at == created_at


def test_saved_resume_response_rejects_storage_filename():
    with pytest.raises(ValidationError):
        SavedResumeResponse.model_validate(
            {
                "id": 4,
                "original_filename": "my-resume.pdf",
                "storage_filename": (
                    "server-generated-resume.pdf"
                ),
                "created_at": datetime.now(timezone.utc),
            }
        )