from sqlalchemy.orm import Session

from app.models.analysis_model import Analysis
from app.models.application_model import (
    Application,
    ApplicationEvent,
)
from app.models.application_schema import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from app.models.cover_letter_model import CoverLetter
from app.models.tailored_resume_model import TailoredResume


class ApplicationLinkNotFoundError(ValueError):
    """Raised when a linked resource is absent or not user-owned."""


def _validate_user_owned_links(
    request: ApplicationCreateRequest | ApplicationUpdateRequest,
    user_id: int,
    db: Session,
) -> None:
    if request.analysis_id is not None:
        analysis = db.query(Analysis).filter(
            Analysis.id == request.analysis_id,
            Analysis.user_id == user_id,
        ).first()

        if analysis is None:
            raise ApplicationLinkNotFoundError(
                "The selected analysis was not found."
            )

    if request.tailored_resume_id is not None:
        tailored_resume = db.query(TailoredResume).filter(
            TailoredResume.id == request.tailored_resume_id,
            TailoredResume.user_id == user_id,
        ).first()

        if tailored_resume is None:
            raise ApplicationLinkNotFoundError(
                "The selected tailored resume was not found."
            )

    if request.cover_letter_id is not None:
        cover_letter = db.query(CoverLetter).filter(
            CoverLetter.id == request.cover_letter_id,
            CoverLetter.user_id == user_id,
        ).first()

        if cover_letter is None:
            raise ApplicationLinkNotFoundError(
                "The selected cover letter was not found."
            )


def create_application_for_user(
    request: ApplicationCreateRequest,
    user_id: int,
    db: Session,
) -> Application:
    _validate_user_owned_links(
        request=request,
        user_id=user_id,
        db=db,
    )

    application = Application(
        user_id=user_id,
        company=request.company,
        role=request.role,
        status=request.status,
        job_url=request.job_url,
        job_description=request.job_description,
        applied_at=request.applied_at,
        next_action_date=request.next_action_date,
        notes=request.notes,
        analysis_id=request.analysis_id,
        tailored_resume_id=request.tailored_resume_id,
        cover_letter_id=request.cover_letter_id,
    )

    try:
        db.add(application)
        db.flush()

        initial_event = ApplicationEvent(
            application_id=application.id,
            user_id=user_id,
            event_type="status_changed",
            previous_status=None,
            new_status=application.status,
            note="Application created.",
        )
        db.add(initial_event)

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(application)

    return application


def get_user_applications(
    user_id: int,
    db: Session,
) -> list[Application]:
    return (
        db.query(Application)
        .filter(Application.user_id == user_id)
        .order_by(Application.updated_at.desc())
        .all()
    )


def get_user_application(
    application_id: int,
    user_id: int,
    db: Session,
) -> Application | None:
    return db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user_id,
    ).first()


def update_user_application(
    application_id: int,
    request: ApplicationUpdateRequest,
    user_id: int,
    db: Session,
) -> Application | None:
    application = get_user_application(
        application_id=application_id,
        user_id=user_id,
        db=db,
    )

    if application is None:
        return None

    _validate_user_owned_links(
        request=request,
        user_id=user_id,
        db=db,
    )

    updates = request.model_dump(exclude_unset=True)
    previous_status = application.status

    for field_name, value in updates.items():
        setattr(application, field_name, value)

    try:
        if (
            "status" in updates
            and application.status != previous_status
        ):
            status_event = ApplicationEvent(
                application_id=application.id,
                user_id=user_id,
                event_type="status_changed",
                previous_status=previous_status,
                new_status=application.status,
                note=(
                    application.notes
                    if "notes" in updates
                    else None
                ),
            )
            db.add(status_event)

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(application)

    return application


def get_user_application_events(
    application_id: int,
    user_id: int,
    db: Session,
) -> list[ApplicationEvent]:
    return (
        db.query(ApplicationEvent)
        .filter(
            ApplicationEvent.application_id
            == application_id,
            ApplicationEvent.user_id == user_id,
        )
        .order_by(ApplicationEvent.created_at.asc())
        .all()
    )


def delete_user_application(
    application_id: int,
    user_id: int,
    db: Session,
) -> Application | None:
    application = get_user_application(
        application_id=application_id,
        user_id=user_id,
        db=db,
    )

    if application is None:
        return None

    try:
        (
            db.query(ApplicationEvent)
            .filter(
                ApplicationEvent.application_id
                == application.id,
                ApplicationEvent.user_id == user_id,
            )
            .delete(synchronize_session=False)
        )

        db.delete(application)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return application