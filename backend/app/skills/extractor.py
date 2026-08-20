import re

from app.skills.taxonomy import (
    SKILL_TAXONOMY,
    SKILL_ALIASES,
)

from app.skills.normalizer import normalize_skill


def get_skill_patterns() -> list[str]:

    patterns = []

    for skills in SKILL_TAXONOMY.values():

        for skill in skills:

            if skill not in patterns:
                patterns.append(skill)

    for alias in SKILL_ALIASES:

        if alias not in patterns:
            patterns.append(alias)

    return patterns


def extract_skills_from_text(
    text: str
) -> list[str]:

    if not text:
        return []

    extracted_skills = []

    normalized_text = text.lower()

    for skill in get_skill_patterns():

        pattern = (
            r"(?<!\w)"
            + re.escape(skill.lower())
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized_text
        ):

            normalized_skill = normalize_skill(
                skill
            )

            if (
                normalized_skill
                and normalized_skill not in extracted_skills
            ):

                extracted_skills.append(
                    normalized_skill
                )

    return extracted_skills