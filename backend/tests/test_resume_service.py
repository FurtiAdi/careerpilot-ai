from unittest.mock import MagicMock, call

import pytest

from app.models.tailored_resume_schema import (
    ResumeEducation,
    TailoredResumeContent,
)
from app.services import resume_service
from types import SimpleNamespace


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


def test_resume_evidence_accepts_punctuation_variation():
    structured_content = make_structured_resume()
    structured_content.experience[0].employer = (
        "Real Company, Inc."
    )
    resume_text = make_resume_text().replace(
        "Real Company",
        "Real Company Inc.",
    )

    resume_service.validate_structured_resume_evidence(
        resume_text=resume_text,
        structured_content=structured_content,
    )


def test_resume_evidence_rejects_partial_word_match():
    structured_content = TailoredResumeContent(
        contact={"full_name": "Ada Lovelace"},
        skills=["SQL"],
    )

    with pytest.raises(
        resume_service.ResumeEvidenceError,
        match="content.skills",
    ):
        resume_service.validate_structured_resume_evidence(
            resume_text=(
                "Ada Lovelace works with PostgreSQL."
            ),
            structured_content=structured_content,
        )


def test_resume_evidence_rejects_invented_content():
    structured_content = make_structured_resume()
    structured_content.experience[0].employer = (
        "Invented Company"
    )

    with pytest.raises(
        resume_service.ResumeEvidenceError,
        match=(
            r"content\.experience\[0\]\.employer"
            r".*unsupported source data"
        ),
    ) as exc:
        resume_service.validate_structured_resume_evidence(
            resume_text=make_resume_text(),
            structured_content=structured_content,
        )

    assert exc.value.field_path == (
        "content.experience[0].employer"
    )


def test_build_grounded_resume_content_discards_unsupported_summary(
    monkeypatch,
):
    structured_content = make_structured_resume()
    structured_content.summary = (
        "Invented professional summary."
    )

    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        MagicMock(return_value=structured_content),
    )

    result = resume_service.build_grounded_resume_content(
        make_resume_text()
    )

    assert result.summary is None


def test_build_grounded_resume_content_repairs_malformed_unicode(
    monkeypatch,
):
    structured_content = make_structured_resume()
    structured_content.experience[0].employer = (
        "Real Comp\x00e4ny"
    )
    resume_text = make_resume_text().replace(
        "Real Company",
        "Real Compäny",
    )

    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        MagicMock(return_value=structured_content),
    )

    result = resume_service.build_grounded_resume_content(
        resume_text
    )

    assert (
        result.experience[0].employer
        == "Real Compäny"
    )


def test_build_grounded_resume_discards_unsupported_education_detail(
    monkeypatch,
):
    structured_content = make_structured_resume()
    structured_content.education = [
        ResumeEducation(
            institution="Real School",
            details=[
                "Verified coursework",
                "Invented coursework",
            ],
        )
    ]
    resume_text = (
        make_resume_text()
        + "\nReal School\nVerified coursework\n"
    )

    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        MagicMock(return_value=structured_content),
    )

    result = resume_service.build_grounded_resume_content(
        resume_text
    )

    assert result.education[0].details == [
        "Verified coursework"
    ]


def test_build_grounded_resume_content_retries_rejected_field(
    monkeypatch,
):
    rejected = make_structured_resume()
    rejected.experience[0].employer = (
        "Invented Company"
    )
    corrected = make_structured_resume()

    mock_structure = MagicMock(
        side_effect=[rejected, corrected]
    )
    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        mock_structure,
    )

    result = resume_service.build_grounded_resume_content(
        make_resume_text()
    )

    assert result is corrected
    assert mock_structure.call_args_list == [
        call(make_resume_text()),
        call(
            make_resume_text(),
            rejected_field=(
                "content.experience[0].employer"
            ),
        ),
    ]


def test_build_grounded_resume_content_retries_only_once(
    monkeypatch,
):
    first_rejected = make_structured_resume()
    first_rejected.experience[0].employer = (
        "Invented Company"
    )
    second_rejected = make_structured_resume()
    second_rejected.experience[0].employer = (
        "Still Invented Company"
    )

    mock_structure = MagicMock(
        side_effect=[
            first_rejected,
            second_rejected,
        ]
    )
    monkeypatch.setattr(
        resume_service,
        "structure_resume_text",
        mock_structure,
    )

    with pytest.raises(
        resume_service.ResumeEvidenceError
    ):
        resume_service.build_grounded_resume_content(
            make_resume_text()
        )

    assert mock_structure.call_count == 2


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


def test_saved_resume_requires_filename():
    user = SimpleNamespace(
        resume_filename=None
    )

    with pytest.raises(
        resume_service.SavedResumeNotFoundError,
        match="required",
    ):
        resume_service.build_grounded_saved_resume_content(
            user
        )


def test_saved_resume_rejects_unsafe_filename(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        resume_service.settings,
        "RESUME_DIR",
        str(tmp_path),
    )

    user = SimpleNamespace(
        resume_filename="../outside.pdf"
    )

    with pytest.raises(
        resume_service.SavedResumeNotFoundError,
        match="not found",
    ):
        resume_service.build_grounded_saved_resume_content(
            user
        )


def test_saved_resume_is_extracted_and_grounded(
    tmp_path,
    monkeypatch,
):
    resume_path = tmp_path / "saved-resume.pdf"
    resume_path.write_bytes(b"%PDF-1.4 test")

    monkeypatch.setattr(
        resume_service.settings,
        "RESUME_DIR",
        str(tmp_path),
    )

    mock_extract = MagicMock(
        return_value="Verified resume text"
    )
    structured_content = make_structured_resume()
    mock_ground = MagicMock(
        return_value=structured_content
    )

    monkeypatch.setattr(
        resume_service,
        "extract_text_from_pdf",
        mock_extract,
    )
    monkeypatch.setattr(
        resume_service,
        "build_grounded_resume_content",
        mock_ground,
    )

    result = (
        resume_service
        .build_grounded_saved_resume_content(
            SimpleNamespace(
                resume_filename="saved-resume.pdf"
            )
        )
    )

    assert result is structured_content
    mock_extract.assert_called_once_with(
        str(resume_path)
    )
    mock_ground.assert_called_once_with(
        "Verified resume text"
    )
