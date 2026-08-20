from dataclasses import dataclass
from app.skills.extractor import extract_skills_from_text

REQUIRED_SECTION_MARKERS = [
    "required skills",
    "required qualifications",
    "required qualifications and skills",
    "requirements",
    "must have",
    "must-have",
    "you must have",
]

PREFERRED_SECTION_MARKERS = [
    "preferred skills",
    "preferred qualifications",
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "bonus skills",
]


@dataclass
class SkillRequirements:
    required: list[str]
    preferred: list[str]




def classify_skill_requirements(
    job_description: str
) -> SkillRequirements:

    text = job_description.lower()

    required_skills = []
    preferred_skills = []

    preferred_start = None

    for marker in PREFERRED_SECTION_MARKERS:

        index = text.find(marker)

        if index != -1:

            if (
                preferred_start is None
                or index < preferred_start
            ):
                preferred_start = index

    if preferred_start is None:

        required_skills = extract_skills_from_text(
            text
        )

    else:

        # Find the beginning of the sentence
        # containing the preferred marker.
        sentence_start = max(
            text.rfind(".", 0, preferred_start),
            text.rfind("!", 0, preferred_start),
            text.rfind("?", 0, preferred_start)
        )

        sentence_start += 1

        required_text = text[:sentence_start]

        preferred_text = text[sentence_start:]

        required_skills = extract_skills_from_text(
            required_text
        )

        preferred_skills = extract_skills_from_text(
            preferred_text
        )

    preferred_skills = [
        skill
        for skill in preferred_skills
        if skill not in required_skills
    ]

    return SkillRequirements(
        required=required_skills,
        preferred=preferred_skills
    )