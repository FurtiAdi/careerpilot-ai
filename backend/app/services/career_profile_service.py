from sqlalchemy.orm import Session

from app.models.career_profile_model import CareerProfile
from app.services.resume_service import (
    SavedResumeNotFoundError,
    build_grounded_career_profile_content_from_record,
)
from app.services.saved_resume_service import (
    get_user_saved_resume,
)


class CareerProfileReviewedError(ValueError):
    """Raised when an extraction would overwrite reviewed content."""


def get_user_career_profile(
    user_id: int,
    db: Session,
) -> CareerProfile | None:
    return db.query(CareerProfile).filter(
        CareerProfile.user_id == user_id,
    ).first()


def extract_and_persist_career_profile_for_user(
    source_resume_id: int,
    user_id: int,
    db: Session,
) -> CareerProfile:
    saved_resume = get_user_saved_resume(
        saved_resume_id=source_resume_id,
        user_id=user_id,
        db=db,
    )

    if saved_resume is None:
        raise SavedResumeNotFoundError(
            "The selected source resume was not found."
        )

    existing_profile = get_user_career_profile(
        user_id=user_id,
        db=db,
    )

    if (
        existing_profile is not None
        and existing_profile.status == "reviewed"
    ):
        raise CareerProfileReviewedError(
            "A reviewed Career Profile cannot be overwritten."
        )

    content = (
        build_grounded_career_profile_content_from_record(
            saved_resume
        )
    )

    if existing_profile is None:
        career_profile = CareerProfile(
            user_id=user_id,
            source_resume_id=saved_resume.id,
            status="draft",
            content=content.model_dump(mode="json"),
        )
        db.add(career_profile)
    else:
        career_profile = existing_profile
        career_profile.source_resume_id = saved_resume.id
        career_profile.status = "draft"
        career_profile.content = content.model_dump(
            mode="json"
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(career_profile)

    return career_profile