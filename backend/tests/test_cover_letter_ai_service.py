from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.models.cover_letter_schema import (
    CoverLetterAIResponse,
)
from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services import ai_service


def make_source_resume() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={
            "full_name": "Ada Lovelace",
        },
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
                "bullets": [
                    "Built Python applications.",
                ],
            }
        ],
        skills=["Python"],
    )


def test_generate_cover_letter_returns_parsed_response(
    monkeypatch,
):
    parsed_response = CoverLetterAIResponse(
        content={
            "opening": "I am applying for the role.",
            "evidence": [
                "Built Python applications.",
            ],
            "motivation": "The role aligns with my experience.",
            "closing": "Thank you for your consideration.",
        }
    )

    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = parsed_response

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=mock_message),
    ]

    mock_parse = MagicMock(return_value=mock_response)
    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        mock_parse,
    )

    result = ai_service.generate_cover_letter(
        resume_content=make_source_resume(),
        job_description="Python engineer role",
        match_snapshot={"match_score": 80},
        tone="professional",
        length="standard",
    )

    assert result == parsed_response
    assert (
        mock_parse.call_args.kwargs["response_format"]
        is CoverLetterAIResponse
    )


def test_generate_cover_letter_rejects_empty_parsed_response(
    monkeypatch,
):
    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = None

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=mock_message),
    ]

    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        MagicMock(return_value=mock_response),
    )

    with pytest.raises(
        ai_service.CoverLetterGenerationError,
        match="could not be parsed",
    ):
        ai_service.generate_cover_letter(
            resume_content=make_source_resume(),
            job_description="Python engineer role",
            match_snapshot={"match_score": 80},
            tone="professional",
            length="standard",
        )


def test_generate_cover_letter_wraps_provider_error(
    monkeypatch,
):
    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        MagicMock(
            side_effect=OpenAIError("Provider error")
        ),
    )

    with pytest.raises(
        ai_service.CoverLetterGenerationError,
        match="temporarily unavailable",
    ):
        ai_service.generate_cover_letter(
            resume_content=make_source_resume(),
            job_description="Python engineer role",
            match_snapshot={"match_score": 80},
            tone="professional",
            length="standard",
        )