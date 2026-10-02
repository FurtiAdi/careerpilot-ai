from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth_dependencies import (
    get_current_user,
)
from app.models.cover_letter_schema import (
    CoverLetterGenerateRequest,
    CoverLetterResponse,
    CoverLetterUpdateRequest,
    CoverLetterContent,
)
from app.models.user_model import User
from app.services.ai_service import (
    CoverLetterGenerationError,
)
from app.services.cover_letter_service import (
    CoverLetterGroundingError,
    create_cover_letter_for_user,
    create_user_cover_letter_version,
    delete_user_cover_letter,
    get_user_cover_letter,
    get_user_cover_letters,
    regenerate_user_cover_letter,
)
from app.services.cover_letter_export_service import (
    render_cover_letter_pdf,
)
from app.services.resume_service import (
    SavedResumeNotFoundError,
)


router = APIRouter(
    prefix="/cover-letters",
    tags=["cover-letters"],
)


@router.post(
    "",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_cover_letter_draft(
    request: CoverLetterGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cover_letter = create_cover_letter_for_user(
            analysis_id=request.analysis_id,
            source_resume_id=request.source_resume_id,
            source_tailored_resume_id=(
                request.source_tailored_resume_id
            ),
            tone=request.tone,
            length=request.length,
            current_user=current_user,
            db=db,
        )
    except SavedResumeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The selected source resume was not found.",
        ) from exc
    except CoverLetterGroundingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Generated cover letter failed "
                "grounding validation."
            ),
        ) from exc    
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The selected tailored resume was not found.",
        ) from exc
    except CoverLetterGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Cover letter generation is "
                "temporarily unavailable."
            ),
        ) from exc

    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return cover_letter


@router.get(
    "",
    response_model=list[CoverLetterResponse],
)
def list_cover_letters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_cover_letters(
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/{cover_letter_id}/export",
    response_class=Response,
)
def export_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cover_letter = get_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        db=db,
    )

    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found.",
        )

    content = CoverLetterContent.model_validate(
        cover_letter.content
    )
    pdf_bytes = render_cover_letter_pdf(content)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                f'filename="cover-letter-{cover_letter.id}.pdf"'
            )
        },
    )


@router.post(
    "/{cover_letter_id}/regenerate",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
)
def regenerate_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cover_letter = regenerate_user_cover_letter(
            cover_letter_id=cover_letter_id,
            user_id=current_user.id,
            db=db,
        )
    except SavedResumeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The original source resume was not found.",
        ) from exc
    except CoverLetterGroundingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Regenerated cover letter failed "
                "grounding validation."
            ),
        ) from exc
    except CoverLetterGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Cover letter generation is "
                "temporarily unavailable."
            ),
        ) from exc

    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found.",
        )

    return cover_letter


@router.get(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
)
def get_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cover_letter = get_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        db=db,
    )

    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found.",
        )

    return cover_letter


@router.patch(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
)
def update_cover_letter(
    cover_letter_id: int,
    request: CoverLetterUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_letter = create_user_cover_letter_version(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        content=request.content,
        status=request.status,
        db=db,
    )

    if updated_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found.",
        )

    return updated_letter


@router.delete("/{cover_letter_id}")
def delete_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_letter = delete_user_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        db=db,
    )

    if deleted_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found.",
        )

    return {
        "message": "Cover letter deleted."
    }