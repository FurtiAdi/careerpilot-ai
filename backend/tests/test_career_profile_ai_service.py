from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.models.career_profile_schema import (
    CareerProfileContent,
)
from app.services import ai_service


def make_career_profile() -> CareerProfileContent:
    return CareerProfileContent(
        contact={
            "full_name": "Ada Lovelace",
        },
        experience=[
            {
                "title": "Software Engineer",
                "employer": "Real Company",
            }
        ],
        skills=["Python"],
    )


def test_structure_career_profile_returns_parsed_content(
    monkeypatch,
):
    parsed_content = make_career_profile()

    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = parsed_content

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

    result = ai_service.structure_career_profile_text(
        "Ada Lovelace\nReal Company\nSoftware Engineer\nPython"
    )

    assert result == parsed_content
    assert (
        mock_parse.call_args.kwargs["response_format"]
        is CareerProfileContent
    )
    assert mock_parse.call_args.kwargs["temperature"] == 0


def test_structure_career_profile_rejects_empty_source():
    with pytest.raises(
        ai_service.CareerProfileStructuringError,
        match="no extractable text",
    ):
        ai_service.structure_career_profile_text("   ")


def test_structure_career_profile_wraps_provider_error(
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
        ai_service.CareerProfileStructuringError,
        match="temporarily unavailable",
    ):
        ai_service.structure_career_profile_text(
            "Ada Lovelace"
        )