import re

from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analysis_model import Analysis
from app.models.cover_letter_model import CoverLetter
from app.models.cover_letter_schema import (
    CoverLetterAIResponse,
    CoverLetterContent,
)
from app.models.user_model import User
from app.services.ai_service import generate_cover_letter
from app.services.resume_service import (
    SavedResumeNotFoundError,
    build_grounded_saved_resume_content_from_record,
)
from app.services.saved_resume_service import (
    get_user_saved_resume,
)
from app.services.tailored_resume_service import (
    build_analysis_match_snapshot,
    get_user_tailored_resume,
)


class CoverLetterGroundingError(ValueError):
    """Raised when generated cover-letter content lacks support."""


NUMBER_PATTERN = re.compile(
    r"(?<!\w)\d+(?:[.,]\d+)?%?(?!\w)"
)


def _content_text(content: CoverLetterContent) -> str:
    return "\n".join(
        [
            content.opening,
            *content.evidence,
            content.motivation,
            content.closing,
        ]
    )


def _source_skills(
    resume_content,
) -> set[str]:
    skills = {
        skill.strip().casefold()
        for skill in resume_content.skills
        if skill.strip()
    }

    for project in resume_content.projects:
        skills.update(
            technology.strip().casefold()
            for technology in project.technologies
            if technology.strip()
        )

    return skills


def validate_cover_letter_grounding(
    source_resume,
    generated: CoverLetterContent,
    match_snapshot: dict[str, object],
) -> None:
    generated_text = _content_text(generated)
    source_text = source_resume.model_dump_json()

    generated_numbers = set(
        NUMBER_PATTERN.findall(generated_text)
    )
    source_numbers = set(
        NUMBER_PATTERN.findall(source_text)
    )

    if not generated_numbers.issubset(source_numbers):
        raise CoverLetterGroundingError(
            "Generated cover letter contains an unsupported quantity."
        )

    missing_skills = {
        str(skill).strip().casefold()
        for skill in (
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
        if str(skill).strip()
    }

    source_skills = _source_skills(source_resume)

    for skill in missing_skills - source_skills:
        if re.search(
            rf"(?<!\w){re.escape(skill)}(?!\w)",
            generated_text,
            flags=re.IGNORECASE,
        ):
            raise CoverLetterGroundingError(
                "Generated cover letter claims a missing skill."
            )


def create_cover_letter_for_user(
    analysis_id: int,
    source_resume_id: int,
    source_tailored_resume_id: int | None,
    tone: str,
    length: str,
    current_user: User,
    db: Session,
) -> CoverLetter | None:
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id,
    ).first()

    if analysis is None:
        return None

    saved_resume = get_user_saved_resume(
        saved_resume_id=source_resume_id,
        user_id=current_user.id,
        db=db,
    )

    if saved_resume is None:
        raise SavedResumeNotFoundError(
            "The selected source resume was not found."
        )

    if source_tailored_resume_id is not None:
        tailored_resume = get_user_tailored_resume(
            tailored_resume_id=source_tailored_resume_id,
            user_id=current_user.id,
            db=db,
        )

        if tailored_resume is None:
            raise ValueError(
                "The selected tailored resume was not found."
            )

    source_content = (
        build_grounded_saved_resume_content_from_record(
            saved_resume
        )
    )

    match_snapshot = build_analysis_match_snapshot(analysis)

    generated = generate_cover_letter(
        resume_content=source_content,
        job_description=analysis.job_description,
        match_snapshot=match_snapshot,
        tone=tone,
        length=length,
    )

    validate_cover_letter_grounding(
        source_resume=source_content,
        generated=generated.content,
        match_snapshot=match_snapshot,
    )

    cover_letter = CoverLetter(
        user_id=current_user.id,
        source_analysis_id=analysis.id,
        source_resume_id=saved_resume.id,
        source_tailored_resume_id=source_tailored_resume_id,
        version_group_id=str(uuid4()),
        version_number=1,
        status="draft",
        tone=tone,
        length=length,
        content=generated.content.model_dump(mode="json"),
    )

    db.add(cover_letter)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(cover_letter)

    return cover_letter

def get_user_cover_letters(
    user_id: int,
    db: Session,
) -> list[CoverLetter]:
    return (
        db.query(CoverLetter)
        .filter(CoverLetter.user_id == user_id)
        .order_by(CoverLetter.updated_at.desc())
        .all()
    )


def get_user_cover_letter(
    cover_letter_id: int,
    user_id: int,
    db: Session,
) -> CoverLetter | None:
    return db.query(CoverLetter).filter(
        CoverLetter.id == cover_letter_id,
        CoverLetter.user_id == user_id,
    ).first()

def create_user_cover_letter_version(
    cover_letter_id: int,
    user_id: int,
    content: CoverLetterContent | None,
    status: str | None,
    db: Session,
) -> CoverLetter | None:
    existing = get_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=user_id,
        db=db,
    )

    if existing is None:
        return None

    latest_version = (
        db.query(
            func.max(CoverLetter.version_number)
        )
        .filter(
            CoverLetter.user_id == user_id,
            CoverLetter.version_group_id
            == existing.version_group_id,
        )
        .scalar()
    )

    new_version = CoverLetter(
        user_id=user_id,
        source_analysis_id=existing.source_analysis_id,
        source_resume_id=existing.source_resume_id,
        source_tailored_resume_id=(
            existing.source_tailored_resume_id
        ),
        version_group_id=existing.version_group_id,
        version_number=(
            latest_version or existing.version_number
        ) + 1,
        status=status or existing.status,
        tone=existing.tone,
        length=existing.length,
        content=(
            content.model_dump(mode="json")
            if content is not None
            else dict(existing.content)
        ),
    )

    db.add(new_version)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(new_version)

    return new_version


def delete_user_cover_letter(
    cover_letter_id: int,
    user_id: int,
    db: Session,
) -> CoverLetter | None:
    cover_letter = get_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=user_id,
        db=db,
    )

    if cover_letter is None:
        return None

    db.delete(cover_letter)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return cover_letter

def regenerate_user_cover_letter(
    cover_letter_id: int,
    user_id: int,
    db: Session,
) -> CoverLetter | None:
    existing = get_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=user_id,
        db=db,
    )

    if existing is None:
        return None

    analysis = db.query(Analysis).filter(
        Analysis.id == existing.source_analysis_id,
        Analysis.user_id == user_id,
    ).first()

    if analysis is None:
        return None

    saved_resume = get_user_saved_resume(
        saved_resume_id=existing.source_resume_id,
        user_id=user_id,
        db=db,
    )

    if saved_resume is None:
        raise SavedResumeNotFoundError(
            "The original source resume was not found."
        )

    source_content = (
        build_grounded_saved_resume_content_from_record(
            saved_resume
        )
    )
    match_snapshot = build_analysis_match_snapshot(analysis)

    generated = generate_cover_letter(
        resume_content=source_content,
        job_description=analysis.job_description,
        match_snapshot=match_snapshot,
        tone=existing.tone,
        length=existing.length,
    )

    validate_cover_letter_grounding(
        source_resume=source_content,
        generated=generated.content,
        match_snapshot=match_snapshot,
    )

    latest_version = (
        db.query(func.max(CoverLetter.version_number))
        .filter(
            CoverLetter.user_id == user_id,
            CoverLetter.version_group_id
            == existing.version_group_id,
        )
        .scalar()
    )

    regenerated_letter = CoverLetter(
        user_id=user_id,
        source_analysis_id=existing.source_analysis_id,
        source_resume_id=existing.source_resume_id,
        source_tailored_resume_id=(
            existing.source_tailored_resume_id
        ),
        version_group_id=existing.version_group_id,
        version_number=(
            latest_version or existing.version_number
        ) + 1,
        status="draft",
        tone=existing.tone,
        length=existing.length,
        content=generated.content.model_dump(mode="json"),
    )

    db.add(regenerated_letter)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(regenerated_letter)

    return regenerated_letter