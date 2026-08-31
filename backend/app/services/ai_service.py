from openai import OpenAI, OpenAIError

from app.models.ai_schema import AIAnalysisResponse
from app.services.ai_prompts import (
    AI_ANALYSIS_SYSTEM_PROMPT,
    build_analysis_prompt,
)

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


class AIAnalysisError(Exception):
    """Raised when the AI response cannot be used safely."""


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