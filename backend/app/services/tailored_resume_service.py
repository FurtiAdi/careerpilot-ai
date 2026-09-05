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