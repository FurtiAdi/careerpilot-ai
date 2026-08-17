from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user_model import User
from app.models.user_schema import UserLogin

from app.services.auth_service import (
    verify_password,
    create_access_token
)

from app.services.user_service import (
    register_user
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

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        return {
            "error": "Invalid email or password"
        }

    valid_password = verify_password(
        user.password,
        existing_user.hashed_password
    )

    if not valid_password:

        return {
            "error": "Invalid email or password"
        }

    access_token = create_access_token(
        data={
            "sub": existing_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }