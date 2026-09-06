from unittest.mock import MagicMock

import pytest

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services import resume_service


def make_structured_resume() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
        },
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
                "start_date": "2022",
                "end_date": "2024",
                "bullets": [
                    "Built Python applications."
                ],
            }
        ],
        skills=["Python"],
    )


def make_resume_text() -> str:
    return """
Ada Lovelace
ada@example.com

Real Company
Software Engineer
2022 - 2024
Built Python applications.

Skills
Python
"""


def test_resume_evidence_accepts_source_backed_content():
    resume_service.validate_structured_resume_evidence(
        resume_text=make_resume_text(),
        structured_content=make_structured_resume(),
    )


def test_resume_evidence_rejects_invented_content():
    structured_content = make_structured_resume()
    structured_content.experience[0].employer = (
        "Invented Company"
    )

    with pytest.raises(
        resume_service.ResumeEvidenceError,
        match="unsupported source data",
    ):
        resume_service.validate_structured_resume_evidence(
            resume_text=make_resume_text(),
            structured_content=structured_content,
        )


def test_build_grounded_resume_content_validates_ai_result(
    monkeypatch,
):
    structured_content = make_structured_resume()

    mock_structure = MagicMock(
        return_value=structured_content
    )
    mock_validate = MagicMock()

    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        mock_structure,
    )
    monkeypatch.setattr(
        resume_service,
        "validate_structured_resume_evidence",
        mock_validate,
    )

    result = resume_service.build_grounded_resume_content(
        "Verified resume text"
    )

    assert result is structured_content
    mock_structure.assert_called_once_with(
        "Verified resume text"
    )
    mock_validate.assert_called_once_with(
        resume_text="Verified resume text",
        structured_content=structured_content,
    )