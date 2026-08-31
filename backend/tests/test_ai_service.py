from unittest.mock import MagicMock

from openai import OpenAIError

from app.models.ai_schema import AIAnalysisResponse
from app.services import ai_service


def test_generate_ai_analysis_returns_parsed_response(monkeypatch):
    parsed_response = AIAnalysisResponse(
        summary="Strong overall match.",
        strengths=["Python", "FastAPI"],
        missing_requirements=["Docker"],
        recommendations=["Improve Docker knowledge"],
    )

    mock_message = MagicMock()
    mock_message.refusal = None
    mock_message.parsed = parsed_response

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=mock_message)
    ]

    mock_parse = MagicMock(
        return_value=mock_response
    )

    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        mock_parse,
    )

    result = ai_service.generate_ai_analysis(
        match_score=80,
        matched_required_skills=[
            "python",
            "fastapi",
        ],
        missing_required_skills=[
            "docker",
        ],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
    )

    assert result == parsed_response


def test_generate_ai_analysis_returns_fallback_on_refusal(
    monkeypatch,
):
    mock_message = MagicMock()
    mock_message.refusal = "Cannot comply"
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

    result = ai_service.generate_ai_analysis(
        match_score=50,
        matched_required_skills=["python"],
        missing_required_skills=["fastapi"],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
    )

    assert (
        result.summary
        == "AI recommendations are temporarily unavailable. "
        "Your deterministic skill-match results are still available."
    )

    assert result.recommendations == [
        "Review the missing required skills shown above.",
        "Try generating AI recommendations again later.",
    ]


def test_generate_ai_analysis_returns_fallback_when_parsed_is_none(
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

    result = ai_service.generate_ai_analysis(
        match_score=70,
        matched_required_skills=["python"],
        missing_required_skills=["docker"],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
    )

    assert "temporarily unavailable" in result.summary
    assert len(result.recommendations) == 2


def test_generate_ai_analysis_returns_fallback_on_openai_error(
    monkeypatch,
):
    monkeypatch.setattr(
        ai_service.client.beta.chat.completions,
        "parse",
        MagicMock(
            side_effect=OpenAIError(
                "Provider error"
            )
        ),
    )

    result = ai_service.generate_ai_analysis(
        match_score=60,
        matched_required_skills=["python"],
        missing_required_skills=["fastapi"],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
    )

    assert isinstance(
        result,
        AIAnalysisResponse,
    )

    assert "temporarily unavailable" in result.summary
    