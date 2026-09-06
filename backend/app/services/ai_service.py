from openai import OpenAI, OpenAIError

from app.models.ai_schema import AIAnalysisResponse
from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
    TailoredResumeContent,
)
from app.services.ai_prompts import (
    AI_ANALYSIS_SYSTEM_PROMPT,
    TAILORED_RESUME_SYSTEM_PROMPT,
    build_analysis_prompt,
    build_tailored_resume_prompt,
    RESUME_STRUCTURE_SYSTEM_PROMPT,
    build_resume_structure_prompt,
)

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


class AIAnalysisError(Exception):
    """Raised when the AI response cannot be used safely."""


class TailoredResumeGenerationError(Exception):
    """Raised when a tailored resume cannot be generated safely."""


class ResumeStructuringError(Exception):
    """Raised when resume text cannot be structured safely."""


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


def structure_resume_text(
    resume_text: str,
) -> TailoredResumeContent:
    if not resume_text.strip():
        raise ResumeStructuringError(
            "The source resume contains no extractable text."
        )

    prompt = build_resume_structure_prompt(
        resume_text
    )

    try:
        response = client.beta.chat.completions.parse(
            model=settings.AI_ANALYSIS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": RESUME_STRUCTURE_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=TailoredResumeContent,
        )

        message = response.choices[0].message

        if message.refusal:
            raise ResumeStructuringError(
                "The AI provider refused to structure the resume."
            )

        if message.parsed is None:
            raise ResumeStructuringError(
                "The structured resume response could not be parsed."
            )

        return message.parsed

    except OpenAIError as exc:
        raise ResumeStructuringError(
            "Resume structuring is temporarily unavailable."
        ) from exc