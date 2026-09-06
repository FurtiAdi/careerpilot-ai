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
from app.models.tailored_resume_schema import (
    TailoredResumeGenerateRequest,
    TailoredResumeResponse,
    TailoredResumeUpdateRequest,
)
from app.models.user_model import User
from app.services.ai_service import (
    TailoredResumeGenerationError,
)
from app.services.tailored_resume_service import (
    TailoredResumeGroundingError,
    create_tailored_resume_for_user,
    get_user_tailored_resume,
    get_user_tailored_resumes,
    create_user_tailored_resume_version,
    delete_user_tailored_resume,
)
from app.services.resume_service import (
    SavedResumeNotFoundError,
)


router = APIRouter(
    prefix="/tailored-resumes",
    tags=["tailored-resumes"],
)


@router.post(
    "",
    response_model=TailoredResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_tailored_resume_draft(
    request: TailoredResumeGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        tailored_resume = create_tailored_resume_for_user(
            analysis_id=request.analysis_id,
            current_user=current_user,
            db=db,
        )
    except SavedResumeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A saved source resume is required.",
        ) from exc
    except TailoredResumeGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Tailored resume generation is "
                "temporarily unavailable."
            ),
        ) from exc
    except TailoredResumeGroundingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Generated resume failed grounding validation."
            ),
        ) from exc

    if tailored_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return tailored_resume


@router.get(
    "",
    response_model=list[TailoredResumeResponse],
)
def list_tailored_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_tailored_resumes(
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/{tailored_resume_id}",
    response_model=TailoredResumeResponse,
)
def get_tailored_resume(
    tailored_resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tailored_resume = get_user_tailored_resume(
        tailored_resume_id=tailored_resume_id,
        user_id=current_user.id,
        db=db,
    )

    if tailored_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found.",
        )

    return tailored_resume


@router.patch(
    "/{tailored_resume_id}",
    response_model=TailoredResumeResponse,
)
def update_tailored_resume(
    tailored_resume_id: int,
    request: TailoredResumeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_resume = create_user_tailored_resume_version(
        tailored_resume_id=tailored_resume_id,
        user_id=current_user.id,
        content=request.content,
        status=request.status,
        db=db,
    )

    if updated_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found.",
        )

    return updated_resume


@router.delete("/{tailored_resume_id}")
def delete_tailored_resume(
    tailored_resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_resume = delete_user_tailored_resume(
        tailored_resume_id=tailored_resume_id,
        user_id=current_user.id,
        db=db,
    )

    if deleted_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found.",
        )

    return {
        "message": "Tailored resume deleted."
    }