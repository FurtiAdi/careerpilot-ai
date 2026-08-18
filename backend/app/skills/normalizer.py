from app.skills.taxonomy import (
    SKILL_ALIASES,
    SKILL_TAXONOMY,
)


def normalize_skill(
    skill: str
) -> str | None:

    normalized = skill.strip().lower()

    if not normalized:
        return None

    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    for skills in SKILL_TAXONOMY.values():

        if normalized in skills:
            return normalized

    return None

def normalize_skills(
    skills: list[str]
) -> list[str]:

    normalized_skills = []

    for skill in skills:

        normalized = normalize_skill(
            skill
        )

        if normalized and normalized not in normalized_skills:
            normalized_skills.append(
                normalized
            )

    return normalized_skills