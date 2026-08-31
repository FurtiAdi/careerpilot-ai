from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user_schema import UserLogin
from app.services.upload_validation import (
    read_validated_pdf,
    read_validated_profile_image,
)
from app.services.user_service import (
    register_user,
    authenticate_user
)

router = APIRouter()


@router.post("/register")
async def register_user_route(

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    resume: UploadFile = File(None),

    profile_picture: UploadFile = File(None),

    db: Session = Depends(get_db)

):
    resume_content = None
    profile_picture_content = None

    if resume is not None:
        resume_content = await read_validated_pdf(
            resume
        )

    if profile_picture is not None:
        profile_picture_content = (
            await read_validated_profile_image(
                profile_picture
            )
        )

    new_user = register_user(
        full_name=full_name,
        email=email,
        password=password,
        resume_content=resume_content,
        profile_picture_content=profile_picture_content,
        profile_picture_content_type=(
            profile_picture.content_type
            if profile_picture
            else None
        ),
        db=db
    )

    if not new_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    access_token = authenticate_user(
        email=user.email,
        password=user.password,
        db=db
    )

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }