import pytest
from pydantic import ValidationError

from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
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