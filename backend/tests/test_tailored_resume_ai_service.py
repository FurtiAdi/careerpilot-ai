from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.models.tailored_resume_schema import (
    TailoredResumeAIResponse,
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
                    "Built Python applications."
                ],
            }
        ],
        skills=["Python"],
    )


def test_generate_tailored_resume_returns_parsed_response(
    monkeypatch,
):
    source_resume = make_source_resume()

    parsed_response = TailoredResumeAIResponse(
        content=source_resume,
        emphasized_items=["Python experience"],
    )

    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = parsed_response

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=mock_message)
    ]

    mock_parse = MagicMock(return_value=mock_response)

    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        mock_parse,
    )

    result = ai_service.generate_tailored_resume(
        resume_content=source_resume,
        job_description="Python role",
        match_snapshot={
            "match_score": 80,
            "missing_required_skills": ["docker"],
        },
    )

    assert result == parsed_response
    assert (
        mock_parse.call_args.kwargs["response_format"]
        is TailoredResumeAIResponse
    )


def test_generate_tailored_resume_rejects_empty_parsed_response(
    monkeypatch,
):
    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = None

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=mock_message)
    ]

    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        MagicMock(return_value=mock_response),
    )

    with pytest.raises(
        ai_service.TailoredResumeGenerationError,
        match="could not be parsed",
    ):
        ai_service.generate_tailored_resume(
            resume_content=make_source_resume(),
            job_description="Python role",
            match_snapshot={"match_score": 80},
        )


def test_generate_tailored_resume_wraps_provider_error(
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
        ai_service.TailoredResumeGenerationError,
        match="temporarily unavailable",
    ):
        ai_service.generate_tailored_resume(
            resume_content=make_source_resume(),
            job_description="Python role",
            match_snapshot={"match_score": 80},
        )