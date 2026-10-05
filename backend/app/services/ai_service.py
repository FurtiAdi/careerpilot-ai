from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel
from openai import OpenAI, OpenAIError

from app.models.ai_schema import AIAnalysisResponse
from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
    TailoredResumeContent,
)
from app.models.career_profile_schema import (
    CareerProfileContent,
)
from app.models.cover_letter_schema import (
    CoverLetterAIResponse,
)
from app.services.ai_prompts import (
    AI_ANALYSIS_SYSTEM_PROMPT,
    TAILORED_RESUME_SYSTEM_PROMPT,
    COVER_LETTER_SYSTEM_PROMPT,
    build_cover_letter_prompt,
    build_analysis_prompt,
    build_tailored_resume_prompt,
    RESUME_STRUCTURE_SYSTEM_PROMPT,
    build_resume_structure_prompt,
    CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT,
    build_career_profile_structure_prompt,
)

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


class AIAnalysisError(Exception):
    """Raised when the AI response cannot be used safely."""


class TailoredResumeGenerationError(Exception):
    """Raised when a tailored resume cannot be generated safely."""

class CoverLetterGenerationError(Exception):
    """Raised when a cover letter cannot be generated safely."""

class ResumeStructuringError(Exception):
    """Raised when resume text cannot be structured safely."""

class CareerProfileStructuringError(Exception):
    """Raised when Career Profile text cannot be structured safely."""


StructuredContent = TypeVar(
    "StructuredContent",
    bound=BaseModel,
)

def generate_ai_analysis(
    match_score: int,
    matched_required_skills: list[str],
    missing_required_skills: list[str],
    matched_preferred_skills: list[str],
    missing_preferred_skills: list[str],
) -> AIAnalysisResponse:

    prompt = build_analysis_prompt(
        match_score=match_score,
        matched_required_skills=matched_required_skills,
        missing_required_skills=missing_required_skills,
        matched_preferred_skills=matched_preferred_skills,
        missing_preferred_skills=missing_preferred_skills,
    )

    try:
        response = client.beta.chat.completions.parse(
            model=settings.AI_ANALYSIS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": AI_ANALYSIS_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=AIAnalysisResponse,
        )

        message = response.choices[0].message

        if message.refusal:
            raise AIAnalysisError(
                "The AI provider refused to generate an analysis."
            )

        if message.parsed is None:
            raise AIAnalysisError(
                "The AI response could not be parsed."
            )

        return message.parsed

    except (AIAnalysisError, OpenAIError):
        return AIAnalysisResponse(
            summary=(
                "AI recommendations are temporarily unavailable. "
                "Your deterministic skill-match results are still available."
            ),
            recommendations=[
                "Review the missing required skills shown above.",
                "Try generating AI recommendations again later.",
            ],
        )


def generate_tailored_resume(
    resume_content: TailoredResumeContent,
    job_description: str,
    match_snapshot: dict[str, object],
) -> TailoredResumeAIResponse:
    prompt = build_tailored_resume_prompt(
        resume_content=resume_content,
        job_description=job_description,
        match_snapshot=match_snapshot,
    )

    try:
        response = client.beta.chat.completions.parse(
            model=settings.AI_ANALYSIS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": TAILORED_RESUME_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=TailoredResumeAIResponse,
        )

        message = response.choices[0].message

        if message.refusal:
            raise TailoredResumeGenerationError(
                "The AI provider refused to tailor the resume."
            )

        if message.parsed is None:
            raise TailoredResumeGenerationError(
                "The tailored resume response could not be parsed."
            )

        return message.parsed

    except OpenAIError as exc:
        raise TailoredResumeGenerationError(
            "Tailored resume generation is temporarily unavailable."
        ) from exc


def generate_cover_letter(
    resume_content: TailoredResumeContent,
    job_description: str,
    match_snapshot: dict[str, object],
    tone: str,
    length: str,
) -> CoverLetterAIResponse:
    prompt = build_cover_letter_prompt(
        resume_content=resume_content,
        job_description=job_description,
        match_snapshot=match_snapshot,
        tone=tone,
        length=length,
    )

    try:
        response = client.beta.chat.completions.parse(
            model=settings.AI_ANALYSIS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": COVER_LETTER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=CoverLetterAIResponse,
        )

        message = response.choices[0].message

        if message.refusal:
            raise CoverLetterGenerationError(
                "The AI provider refused to generate a cover letter."
            )

        if message.parsed is None:
            raise CoverLetterGenerationError(
                "The cover letter response could not be parsed."
            )

        return message.parsed

    except OpenAIError as exc:
        raise CoverLetterGenerationError(
            "Cover letter generation is temporarily unavailable."
        ) from exc


def _structure_source_text(
    source_text: str,
    rejected_field: str | None,
    *,
    response_format: type[StructuredContent],
    prompt_builder: Callable[
        [str, str | None],
        str,
    ],
    system_prompt: str,
    error_class: type[Exception],
    source_label: str,
) -> StructuredContent:
    if not source_text.strip():
        raise error_class(
            "The source resume contains no extractable text."
        )

    prompt = prompt_builder(
        source_text,
        rejected_field = rejected_field,
    )

    try:
        response = client.beta.chat.completions.parse(
            model=settings.AI_ANALYSIS_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=response_format,
        )

        message = response.choices[0].message

        if message.refusal:
            raise error_class(
                f"The AI provider refused to structure the "
                f"{source_label.casefold()}."
            )

        if message.parsed is None:
            raise error_class(
                f"The structured {source_label.casefold()} "
                "response could not be parsed."
            )

        return message.parsed

    except OpenAIError as exc:
        raise error_class(
            f"{source_label} structuring is temporarily unavailable."
        ) from exc


def structure_resume_text(
    resume_text: str,
    rejected_field: str | None = None,
) -> TailoredResumeContent:
    return _structure_source_text(
        resume_text,
        rejected_field,
        response_format=TailoredResumeContent,
        prompt_builder=build_resume_structure_prompt,
        system_prompt=RESUME_STRUCTURE_SYSTEM_PROMPT,
        error_class=ResumeStructuringError,
        source_label="Resume",
    )


def structure_career_profile_text(
    resume_text: str,
    rejected_field: str | None = None,
) -> CareerProfileContent:
    return _structure_source_text(
        resume_text,
        rejected_field,
        response_format=CareerProfileContent,
        prompt_builder=build_career_profile_structure_prompt,
        system_prompt=CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT,
        error_class=CareerProfileStructuringError,
        source_label="Career Profile",
    )