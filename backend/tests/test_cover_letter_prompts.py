from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services.ai_prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    build_cover_letter_prompt,
)


def test_cover_letter_system_prompt_forbids_fabrication():
    assert "Never invent or infer" in COVER_LETTER_SYSTEM_PROMPT
    assert "company-specific claims" in COVER_LETTER_SYSTEM_PROMPT
    assert "Missing skills must remain gaps" in (
        COVER_LETTER_SYSTEM_PROMPT
    )


def test_cover_letter_prompt_contains_verified_context():
    resume_content = TailoredResumeContent(
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

    prompt = build_cover_letter_prompt(
        resume_content=resume_content,
        job_description="Python engineer role at Example Corp.",
        match_snapshot={
            "match_score": 80,
            "missing_required_skills": ["docker"],
        },
        tone="professional",
        length="standard",
    )

    assert "Real Company" in prompt
    assert "Python engineer role at Example Corp." in prompt
    assert '"match_score": 80' in prompt
    assert '"docker"' in prompt
    assert "Use a professional tone" in prompt
    assert "standard length" in prompt

    normalized_prompt = " ".join(prompt.split())
    
    assert (
        "Do not make company-specific claims"
        in normalized_prompt
    )