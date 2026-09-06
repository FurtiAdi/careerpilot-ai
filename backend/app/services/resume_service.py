import os
from collections.abc import Iterator

import fitz

from app.core.config import settings
from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.models.user_model import User
from app.services.ai_service import structure_resume_text


class ResumeEvidenceError(ValueError):
    """Raised when structured data lacks source evidence."""


class SavedResumeNotFoundError(FileNotFoundError):
    """Raised when a user's saved resume cannot be loaded."""


def _normalize_evidence(value: str) -> str:
    return " ".join(
        value.casefold().split()
    )


def _iter_string_values(
    value: object,
) -> Iterator[str]:
    if isinstance(value, str):
        yield value
        return

    if isinstance(value, dict):
        for nested_value in value.values():
            yield from _iter_string_values(
                nested_value
            )
        return

    if isinstance(value, list):
        for nested_value in value:
            yield from _iter_string_values(
                nested_value
            )


def validate_structured_resume_evidence(
    resume_text: str,
    structured_content: TailoredResumeContent,
) -> None:
    normalized_source = _normalize_evidence(
        resume_text
    )

    for value in _iter_string_values(
        structured_content.model_dump(
            mode="json"
        )
    ):
        normalized_value = _normalize_evidence(
            value
        )

        if (
            normalized_value
            and normalized_value not in normalized_source
        ):
            raise ResumeEvidenceError(
                "Structured resume content contains "
                "unsupported source data."
            )


def build_grounded_resume_content(
    resume_text: str,
) -> TailoredResumeContent:
    structured_content = structure_resume_text(
        resume_text
    )

    validate_structured_resume_evidence(
        resume_text=resume_text,
        structured_content=structured_content,
    )

    return structured_content


def extract_text_from_pdf(pdf_path: str):

    document = fitz.open(pdf_path)

    extracted_text = ""

    for page in document:

        extracted_text += page.get_text()

    document.close()

    return extracted_text


def build_grounded_saved_resume_content(
    current_user: User,
) -> TailoredResumeContent:
    filename = current_user.resume_filename

    if not filename:
        raise SavedResumeNotFoundError(
            "A saved source resume is required."
        )

    upload_directory = os.path.abspath(
        settings.RESUME_DIR
    )
    resume_path = os.path.abspath(
        os.path.join(
            upload_directory,
            filename,
        )
    )

    if not resume_path.startswith(
        upload_directory + os.sep
    ):
        raise SavedResumeNotFoundError(
            "The saved source resume was not found."
        )

    if not os.path.isfile(resume_path):
        raise SavedResumeNotFoundError(
            "The saved source resume was not found."
        )

    resume_text = extract_text_from_pdf(
        resume_path
    )

    return build_grounded_resume_content(
        resume_text
    )