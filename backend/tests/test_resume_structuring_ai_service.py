from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services import ai_service


def make_structured_resume() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={
            "full_name": "Ada Lovelace",
        },
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
            }
        ],
        skills=["Python"],
    )


def test_structure_resume_text_returns_parsed_content(
    monkeypatch,
):
    parsed = make_structured_resume()

    message = MagicMock(
        refusal=None,
        parsed=parsed,
    )
    response = MagicMock()
    response.choices = [
        MagicMock(message=message)
    ]

    mock_parse = MagicMock(return_value=response)
    mock_prompt = MagicMock(
        return_value="Correction prompt"
    )
    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        mock_parse,
    )
    monkeypatch.setattr(
        ai_service,
        "build_resume_structure_prompt",
        mock_prompt,
    )

    result = ai_service.structure_resume_text(
        "Ada worked at Real Company using Python.",
        rejected_field=(
            "content.experience[0].employer"
        ),
    )

    assert result == parsed
    mock_prompt.assert_called_once_with(
        "Ada worked at Real Company using Python.",
        rejected_field=(
            "content.experience[0].employer"
        ),
    )
    assert (
        mock_parse.call_args.kwargs["response_format"]
        is TailoredResumeContent
    )
    assert (
        mock_parse.call_args.kwargs["temperature"]
        == 0
    )


def test_structure_resume_text_rejects_empty_text():
    with pytest.raises(
        ai_service.ResumeStructuringError,
        match="no extractable text",
    ):
        ai_service.structure_resume_text("   ")


def test_structure_resume_text_rejects_unparsed_response(
    monkeypatch,
):
    message = MagicMock(
        refusal=None,
        parsed=None,
    )
    response = MagicMock()
    response.choices = [
        MagicMock(message=message)
    ]

    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        MagicMock(return_value=response),
    )

    with pytest.raises(
        ai_service.ResumeStructuringError,
        match="could not be parsed",
    ):
        ai_service.structure_resume_text(
            "Resume text"
        )


def test_structure_resume_text_wraps_provider_error(
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
        ai_service.ResumeStructuringError,
        match="temporarily unavailable",
    ):
        ai_service.structure_resume_text(
            "Resume text"
        )
