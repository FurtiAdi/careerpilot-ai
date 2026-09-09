import os
import logging
import re
import unicodedata

from collections.abc import Iterator

import fitz

from app.core.config import settings
from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.models.user_model import User
from app.services.ai_service import structure_resume_text

logger = logging.getLogger(__name__)

MALFORMED_UNICODE_PATTERN = re.compile(
    r"\x00([0-9a-fA-F]{2})"
)

class ResumeEvidenceError(ValueError):
    """Raised when structured data lacks source evidence."""

    def __init__(self, field_path: str):
        self.field_path = field_path
        super().__init__(
            f"Structured resume field {field_path} "
            "contains unsupported source data."
        )


class SavedResumeNotFoundError(FileNotFoundError):
    """Raised when a user's saved resume cannot be loaded."""


def _normalize_evidence(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKC",
        value,
    ).casefold()

    normalized = re.sub(
        r"[^\w+#]+",
        " ",
        normalized,
    )

    return " ".join(normalized.split())


def _iter_string_values(
    value: object,
    path: str = "content",
) -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
        return

    if isinstance(value, dict):
        for key, nested_value in value.items():
            yield from _iter_string_values(
                nested_value,
                f"{path}.{key}",
            )
        return

    if isinstance(value, list):
        for index, nested_value in enumerate(value):
            yield from _iter_string_values(
                nested_value,
                f"{path}[{index}]",
            )


def validate_structured_resume_evidence(
    resume_text: str,
    structured_content: TailoredResumeContent,
) -> None:
    normalized_source = _normalize_evidence(
        resume_text
    )

    for field_path, value in _iter_string_values(
        structured_content.model_dump(
            mode="json"
        )
    ):
        normalized_value = _normalize_evidence(
            value
        )

        if (
            normalized_value
            and
            (f" {normalized_value} "
                not in f" {normalized_source} "
            )
        ):
            logger.warning(
                "Structured resume evidence rejected field %s",
                field_path,
            )
            raise ResumeEvidenceError(field_path)


def _repair_malformed_unicode(
    value: object,
) -> object:
    if isinstance(value, str):
        return MALFORMED_UNICODE_PATTERN.sub(
            lambda match: chr(
                int(match.group(1), 16)
            ),
            value,
        )

    if isinstance(value, dict):
        return {
            key: _repair_malformed_unicode(nested)
            for key, nested in value.items()
        }

    if isinstance(value, list):
        return [
            _repair_malformed_unicode(nested)
            for nested in value
        ]

    return value


def _repair_structured_resume_encoding(
    content: TailoredResumeContent,
) -> TailoredResumeContent:
    serialized = content.model_dump(mode="json")
    repaired = _repair_malformed_unicode(
        serialized
    )

    if repaired == serialized:
        return content

    return TailoredResumeContent.model_validate(
        repaired
    )


def _discard_unsupported_education_details(
    resume_text: str,
    content: TailoredResumeContent,
) -> TailoredResumeContent:
    normalized_source = _normalize_evidence(
        resume_text
    )
    serialized = content.model_dump(mode="json")
    changed = False

    for education_index, education in enumerate(
        serialized["education"]
    ):
        supported_details = []

        for detail_index, detail in enumerate(
            education["details"]
        ):
            normalized_detail = _normalize_evidence(
                detail
            )

            if (
                not normalized_detail
                or (
                    f" {normalized_detail} "
                    in f" {normalized_source} "
                )
            ):
                supported_details.append(detail)
                continue

            logger.warning(
                "Discarding unsupported structured resume "
                "field content.education[%s].details[%s]",
                education_index,
                detail_index,
            )
            changed = True

        education["details"] = supported_details

    if not changed:
        return content

    return TailoredResumeContent.model_validate(
        serialized
    )


def _discard_unsupported_summary(
    resume_text: str,
    structured_content: TailoredResumeContent,
) -> TailoredResumeContent:
    if (
        structured_content.summary
        and (
            f" {_normalize_evidence(structured_content.summary)} "
            not in f" {_normalize_evidence(resume_text)} "
        )
    ):
        logger.warning(
            "Discarding unsupported structured resume "
            "field content.summary"
        )
        return structured_content.model_copy(
            update={"summary": None}
        )

    return structured_content


def build_grounded_resume_content(
    resume_text: str,
) -> TailoredResumeContent:
    structured_content = structure_resume_text(
        resume_text
    )
    structured_content = _repair_structured_resume_encoding(
        structured_content
    )
    structured_content = (
        _discard_unsupported_education_details(
            resume_text,
            structured_content,
        )
    )
    structured_content = _discard_unsupported_summary(
        resume_text,
        structured_content,
    )

    try:
        validate_structured_resume_evidence(
            resume_text=resume_text,
            structured_content=structured_content,
        )
    except ResumeEvidenceError as exc:
        logger.warning(
            "Retrying resume structuring after rejected "
            "field %s",
            exc.field_path,
        )

        structured_content = structure_resume_text(
            resume_text,
            rejected_field=exc.field_path,
        )
        structured_content = _repair_structured_resume_encoding(
            structured_content
        )
        structured_content = (
            _discard_unsupported_education_details(
                resume_text,
                structured_content,
            )
        )
        structured_content = _discard_unsupported_summary(
            resume_text,
            structured_content,
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
