import re

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.skills.normalizer import normalize_skill
from app.models.analysis_model import Analysis
from app.skills.requirements import (
    classify_skill_requirements,
)
from app.skills.scorer import calculate_match_score


def build_analysis_match_snapshot(
    analysis: Analysis,
) -> dict:
    candidate_skills = [
        skill.strip()
        for skill in (
            analysis.candidate_skills or ""
        ).split(",")
        if skill.strip()
    ]

    requirements = classify_skill_requirements(
        analysis.job_description
    )

    return calculate_match_score(
        required_skills=requirements.required,
        preferred_skills=requirements.preferred,
        candidate_skills=candidate_skills,
    )

class TailoredResumeGroundingError(ValueError):
    """Raised when generated content violates source facts."""


NUMBER_PATTERN = re.compile(
    r"(?<!\w)\d+(?:[.,]\d+)?%?(?!\w)"
)


def _normalized_text(value: str | None) -> str | None:
    if value is None:
        return None

    return value.strip().casefold()


def _canonical_skills(skills: list[str]) -> set[str]:
    return {
        normalize_skill(skill)
        or skill.strip().casefold()
        for skill in skills
        if skill.strip()
    }


def _experience_facts(
    content: TailoredResumeContent,
) -> set[tuple]:
    return {
        (
            _normalized_text(item.employer),
            _normalized_text(item.title),
            _normalized_text(item.location),
            _normalized_text(item.start_date),
            _normalized_text(item.end_date),
        )
        for item in content.experience
    }


def _education_facts(
    content: TailoredResumeContent,
) -> set[tuple]:
    return {
        (
            _normalized_text(item.institution),
            _normalized_text(item.degree),
            _normalized_text(item.field_of_study),
            _normalized_text(item.start_date),
            _normalized_text(item.end_date),
        )
        for item in content.education
    }


def _project_names(
    content: TailoredResumeContent,
) -> set[str | None]:
    return {
        _normalized_text(item.name)
        for item in content.projects
    }


def _optional_section_headings(
    content: TailoredResumeContent,
) -> set[str | None]:
    return {
        _normalized_text(item.heading)
        for item in content.optional_sections
    }


def _resume_technologies(
    content: TailoredResumeContent,
) -> set[str]:
    technologies = list(content.skills)

    for project in content.projects:
        technologies.extend(project.technologies)

    return _canonical_skills(technologies)


def _numbers(
    content: TailoredResumeContent,
) -> set[str]:
    return set(
        NUMBER_PATTERN.findall(
            content.model_dump_json()
        )
    )


def validate_tailored_resume_grounding(
    source: TailoredResumeContent,
    generated: TailoredResumeContent,
    match_snapshot: dict[str, object],
) -> None:
    if generated.contact != source.contact:
        raise TailoredResumeGroundingError(
            "Generated contact information differs from the source."
        )

    if not _experience_facts(generated).issubset(
        _experience_facts(source)
    ):
        raise TailoredResumeGroundingError(
            "Generated experience contains unsupported facts."
        )

    if not _education_facts(generated).issubset(
        _education_facts(source)
    ):
        raise TailoredResumeGroundingError(
            "Generated education contains unsupported facts."
        )

    if not _project_names(generated).issubset(
        _project_names(source)
    ):
        raise TailoredResumeGroundingError(
            "Generated projects contain unsupported names."
        )

    if not _optional_section_headings(generated).issubset(
        _optional_section_headings(source)
    ):
        raise TailoredResumeGroundingError(
            "Generated resume contains unsupported sections."
        )

    generated_skills = _resume_technologies(generated)
    source_skills = _resume_technologies(source)

    if not generated_skills.issubset(source_skills):
        raise TailoredResumeGroundingError(
            "Generated resume contains unsupported skills."
        )

    missing_skills = _canonical_skills(
        list(
            match_snapshot.get(
                "missing_required_skills",
                [],
            )
        )
        + list(
            match_snapshot.get(
                "missing_preferred_skills",
                [],
            )
        )
    )

    if generated_skills.intersection(missing_skills):
        raise TailoredResumeGroundingError(
            "Generated resume claims a missing skill."
        )

    if not _numbers(generated).issubset(
        _numbers(source)
    ):
        raise TailoredResumeGroundingError(
            "Generated resume contains an unsupported quantity."
        )