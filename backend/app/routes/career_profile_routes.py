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
from app.models.career_profile_schema import (
    CareerProfileExtractRequest,
    CareerProfileResponse,
)
from app.models.user_model import User
from app.services.ai_service import (
    CareerProfileStructuringError,
)
from app.services.career_profile_service import (
    CareerProfileReviewedError,
    extract_and_persist_career_profile_for_user,
    get_user_career_profile,
)
from app.services.resume_service import (
    ResumeEvidenceError,
    SavedResumeNotFoundError,
)


router = APIRouter(
    prefix="/career-profiles",
    tags=["career-profiles"],
)


@router.post(
    "/extract",
    response_model=CareerProfileResponse,
)
def extract_career_profile(
    request: CareerProfileExtractRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return extract_and_persist_career_profile_for_user(
            source_resume_id=request.source_resume_id,
            user_id=current_user.id,
            db=db,
        )
    except SavedResumeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A saved source resume is required.",
        ) from exc
    except CareerProfileStructuringError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Career Profile extraction is "
                "temporarily unavailable."
            ),
        ) from exc
    except ResumeEvidenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Extracted Career Profile failed "
                "source validation."
            ),
        ) from exc
    except CareerProfileReviewedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A reviewed Career Profile cannot be "
                "overwritten."
            ),
        ) from exc


@router.get(
    "/me",
    response_model=CareerProfileResponse,
)
def get_current_career_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    career_profile = get_user_career_profile(
        user_id=current_user.id,
        db=db,
    )

    if career_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career Profile not found.",
        )

    return career_profile