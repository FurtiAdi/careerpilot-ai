from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user_model import User
from app.models.user_schema import UserLogin

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter()


@router.post("/register")
def register_user(

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    resume: UploadFile = File(None),

    profile_picture: UploadFile = File(None),

    db: Session = Depends(get_db)

):

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:

        return {
            "error": "Email already exists"
        }

    hashed_password = hash_password(password)

    resume_filename = None

    profile_picture_filename = None

    if resume:

        resume_filename = resume.filename

        with open(
            f"uploads/resumes/{resume_filename}",
            "wb"
        ) as buffer:

            import shutil

            shutil.copyfileobj(
                resume.file,
                buffer
            )

    if profile_picture:

        profile_picture_filename = (
            profile_picture.filename
        )

        with open(
            f"uploads/profile_pictures/{profile_picture_filename}",
            "wb"
        ) as buffer:

            import shutil

            shutil.copyfileobj(
                profile_picture.file,
                buffer
            )

    new_user = User(

        full_name=full_name,

        email=email,

        hashed_password=hashed_password,

        resume_filename=resume_filename,

        profile_picture_filename=profile_picture_filename
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

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