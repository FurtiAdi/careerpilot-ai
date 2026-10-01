from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth_dependencies import (
    get_current_user,
)
from app.models.saved_resume_schema import (
    SavedResumeResponse,
)
from app.models.user_model import User
from app.services.saved_resume_service import (
    create_saved_resume,
    get_user_saved_resumes,
)
from app.services.upload_validation import (
    read_validated_pdf,
)


router = APIRouter(
    prefix="/saved-resumes",
    tags=["saved-resumes"],
)


@router.post(
    "",
    response_model=SavedResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_saved_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await read_validated_pdf(file)

    return create_saved_resume(
        user_id=current_user.id,
        original_filename=file.filename or "resume.pdf",
        content=content,
        db=db,
    )


@router.get(
    "",
    response_model=list[SavedResumeResponse],
)
def list_saved_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_saved_resumes(
        user_id=current_user.id,
        db=db,
    )
