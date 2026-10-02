from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth_dependencies import (
    get_current_user,
)
from app.models.application_schema import (
    ApplicationCreateRequest,
    ApplicationEventResponse,
    ApplicationResponse,
    ApplicationUpdateRequest,
)
from app.models.user_model import User
from app.services.application_service import (
    ApplicationLinkNotFoundError,
    create_application_for_user,
    delete_user_application,
    get_user_application,
    get_user_application_events,
    get_user_applications,
    update_user_application,
)


router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    request: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_application_for_user(
            request=request,
            user_id=current_user.id,
            db=db,
        )
    except ApplicationLinkNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_applications(
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/{application_id}/events",
    response_model=list[ApplicationEventResponse],
)
def list_application_events(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_application_events(
        application_id=application_id,
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_user_application(
        application_id=application_id,
        user_id=current_user.id,
        db=db,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    return application


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: int,
    request: ApplicationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        application = update_user_application(
            application_id=application_id,
            request=request,
            user_id=current_user.id,
            db=db,
        )
    except ApplicationLinkNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    return application


@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = delete_user_application(
        application_id=application_id,
        user_id=current_user.id,
        db=db,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    return {
        "message": "Application deleted."
    }