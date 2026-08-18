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

from app.services.user_service import (
    register_user,
    authenticate_user
)

router = APIRouter()


@router.post("/register")
def register_user_route(

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    resume: UploadFile = File(None),

    profile_picture: UploadFile = File(None),

    db: Session = Depends(get_db)

):

    new_user = register_user(
        full_name=full_name,
        email=email,
        password=password,
        resume=resume,
        profile_picture=profile_picture,
        db=db
    )

    if not new_user:

        return {
            "error": "Email already exists"
        }

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