from app.services.ai_prompts import (
    CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT,
    build_career_profile_structure_prompt,
)


def test_career_profile_system_prompt_forbids_fabrication():
    assert (
        "Never invent, infer, or complete missing"
        in CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT
    )
    assert "certificates" in (
        CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT
    )
    assert "copied verbatim" in (
        CAREER_PROFILE_STRUCTURE_SYSTEM_PROMPT
    )


def test_career_profile_prompt_contains_source_and_retry_rule():
    prompt = build_career_profile_structure_prompt(
        "Ada Lovelace\nReal Company\nPython",
        rejected_field="content.skills[0]",
    )

    assert "Ada Lovelace" in prompt
    assert "Real Company" in prompt
    assert "content.skills[0]" in prompt
    assert "headline" in prompt
    assert "certificates" in prompt