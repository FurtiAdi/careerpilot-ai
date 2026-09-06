from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services.ai_prompts import (
    TAILORED_RESUME_SYSTEM_PROMPT,
    build_tailored_resume_prompt,
    RESUME_STRUCTURE_SYSTEM_PROMPT,
    build_resume_structure_prompt,
)


def test_tailored_resume_system_prompt_forbids_fabrication():
    assert "Never invent" in TAILORED_RESUME_SYSTEM_PROMPT
    assert (
        "Missing skills must remain gaps"
        in TAILORED_RESUME_SYSTEM_PROMPT
    )
    assert (
        "untrusted reference data"
        in TAILORED_RESUME_SYSTEM_PROMPT
    )


def test_tailored_resume_prompt_contains_verified_context():
    resume_content = TailoredResumeContent(
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

    match_snapshot = {
        "match_score": 80,
        "matched_required_skills": ["python"],
        "missing_required_skills": ["docker"],
    }

    prompt = build_tailored_resume_prompt(
        resume_content=resume_content,
        job_description="Python and Docker role",
        match_snapshot=match_snapshot,
    )

    assert "Real Company" in prompt
    assert "Python and Docker role" in prompt
    assert '"match_score": 80' in prompt
    assert '"docker"' in prompt
    assert "Do not add unsupported facts" in prompt


def test_resume_structure_system_prompt_forbids_invention():
    assert (
        "Never invent, infer, or complete"
        in RESUME_STRUCTURE_SYSTEM_PROMPT
    )
    assert (
        "untrusted reference data"
        in RESUME_STRUCTURE_SYSTEM_PROMPT
    )


def test_resume_structure_prompt_contains_source_text():
    prompt = build_resume_structure_prompt(
        "Ada worked at Real Company using Python."
    )

    assert "Real Company" in prompt
    assert "Python" in prompt
    assert "Do not infer missing" in prompt