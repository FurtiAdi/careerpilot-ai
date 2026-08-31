import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.models.ai_schema import AIAnalysisResponse


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class AIAnalysisError(Exception):
    """Raised when the AI response cannot be used safely."""


def generate_ai_analysis(
    job_description: str,
    candidate_skills: list[str]
) -> AIAnalysisResponse:

    prompt = f"""
Analyze the following job description and candidate skills.

Job Description:
{job_description}

Candidate Skills:
{candidate_skills}
"""

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI career assistant. "
                        "Provide concise, practical career advice."
                    ),
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