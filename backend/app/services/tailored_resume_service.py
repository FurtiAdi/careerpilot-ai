import re

from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.tailored_resume_model import TailoredResume
from app.models.user_model import User
from app.services.ai_service import generate_tailored_resume
from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.skills.normalizer import normalize_skill
from app.models.analysis_model import Analysis
from app.skills.requirements import (
    classify_skill_requirements,
)
from app.skills.scorer import calculate_match_score
from app.services.resume_service import (
    build_grounded_saved_resume_content,
)

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


def create_tailored_resume_for_user(
    analysis_id: int,
    current_user: User,
    db: Session,
) -> TailoredResume | None:
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id,
    ).first()

    if analysis is None:
        return None

    source_content = (
        build_grounded_saved_resume_content(
            current_user
        )
    )

    match_snapshot = build_analysis_match_snapshot(
        analysis
    )

    generated = generate_tailored_resume(
        resume_content=source_content,
        job_description=analysis.job_description,
        match_snapshot=match_snapshot,
    )

    validate_tailored_resume_grounding(
        source=source_content,
        generated=generated.content,
        match_snapshot=match_snapshot,
    )

    tailored_resume = TailoredResume(
        user_id=current_user.id,
        source_analysis_id=analysis.id,
        source_resume_filename=(
            current_user.resume_filename
        ),
        version_group_id=str(uuid4()),
        version_number=1,
        status="draft",
        content=generated.content.model_dump(
            mode="json"
        ),
        emphasized_items=generated.emphasized_items,
        reordered_items=generated.reordered_items,
        match_snapshot=match_snapshot,
    )

    db.add(tailored_resume)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(tailored_resume)

    return tailored_resume


def get_user_tailored_resumes(
    user_id: int,
    db: Session,
) -> list[TailoredResume]:
    return (
        db.query(TailoredResume)
        .filter(TailoredResume.user_id == user_id)
        .order_by(TailoredResume.updated_at.desc())
        .all()
    )


def get_user_tailored_resume(
    tailored_resume_id: int,
    user_id: int,
    db: Session,
) -> TailoredResume | None:
    return db.query(TailoredResume).filter(
        TailoredResume.id == tailored_resume_id,
        TailoredResume.user_id == user_id,
    ).first()


def create_user_tailored_resume_version(
    tailored_resume_id: int,
    user_id: int,
    content: TailoredResumeContent | None,
    status: str | None,
    db: Session,
) -> TailoredResume | None:
    existing = get_user_tailored_resume(
        tailored_resume_id=tailored_resume_id,
        user_id=user_id,
        db=db,
    )

    if existing is None:
        return None

    latest_version = (
        db.query(
            func.max(TailoredResume.version_number)
        )
        .filter(
            TailoredResume.user_id == user_id,
            TailoredResume.version_group_id
            == existing.version_group_id,
        )
        .scalar()
    )

    new_version = TailoredResume(
        user_id=user_id,
        source_analysis_id=existing.source_analysis_id,
        source_resume_filename=(
            existing.source_resume_filename
        ),
        version_group_id=existing.version_group_id,
        version_number=(
            latest_version or existing.version_number
        ) + 1,
        status=status or existing.status,
        content=(
            content.model_dump(mode="json")
            if content is not None
            else dict(existing.content)
        ),
        emphasized_items=list(
            existing.emphasized_items
        ),
        reordered_items=list(
            existing.reordered_items
        ),
        match_snapshot=dict(existing.match_snapshot),
    )

    db.add(new_version)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(new_version)

    return new_version


def delete_user_tailored_resume(
    tailored_resume_id: int,
    user_id: int,
    db: Session,
) -> TailoredResume | None:
    tailored_resume = get_user_tailored_resume(
        tailored_resume_id=tailored_resume_id,
        user_id=user_id,
        db=db,
    )

    if tailored_resume is None:
        return None

    db.delete(tailored_resume)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return tailored_resume