import os
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.user_model import User

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

from app.services.upload_filenames import (
    generate_profile_picture_filename,
)


def authenticate_user(
    email: str,
    password: str,
    db: Session
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    valid_password = verify_password(
        password,
        user.hashed_password
    )

    if not valid_password:
        return None

    access_token = create_access_token(
        data={
            "sub": user.email
        }
    )

    return access_token

def register_user(
    full_name: str,
    email: str,
    password: str,
    resume: UploadFile | None,
    profile_picture: UploadFile | None,
    db: Session
):

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:

        return None

    hashed_password = hash_password(
        password
    )

    resume_filename = None
    profile_picture_filename = None

    if resume:

        resume_filename = resume.filename

        with open(
            f"uploads/resumes/{resume_filename}",
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                resume.file,
                buffer
            )

    if profile_picture:

        os.makedirs(
            "uploads/profile_pictures",
            exist_ok=True,
        )

        profile_picture_filename = (
            generate_profile_picture_filename(
                profile_picture
            )
        )

        with open(
            f"uploads/profile_pictures/{profile_picture_filename}",
            "wb"
        ) as buffer:

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

    return new_user