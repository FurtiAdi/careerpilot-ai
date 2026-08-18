from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user_model import User
from app.dependencies.auth_dependencies import get_current_user
from app.services.profile_service import (
    get_user_profile,
    save_profile_picture,
    get_profile_stats
)

router = APIRouter()

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(
        get_current_user
    )
):

    return get_user_profile(
        current_user
    )

@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return save_profile_picture(
        file=file,
        current_user=current_user,
        db=db
    )


@router.get("/profile-stats")
def get_profile_stats_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return get_profile_stats(
        current_user=current_user,
        db=db
    )