import os

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.user_model import User

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

from app.services.upload_filenames import (
    generate_profile_picture_filename,
    generate_resume_filename,
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
    resume_content: bytes | None,
    profile_picture_content: bytes | None,
    profile_picture_content_type: str | None,
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
    resume_file_path = None
    profile_picture_file_path = None    

    if resume_content:

        os.makedirs(
            settings.RESUME_DIR,
            exist_ok=True,
        )

        resume_filename = generate_resume_filename()
        resume_file_path = (
            os.path.join(
                settings.RESUME_DIR,
                resume_filename,
            )
        )

        with open(
            resume_file_path,
            "wb"
        ) as buffer:

            buffer.write(resume_content)

    if (
        profile_picture_content
        and profile_picture_content_type
    ):
        os.makedirs(
            settings.PROFILE_PICTURE_DIR,
            exist_ok=True,
        )

        profile_picture_filename = (
            generate_profile_picture_filename(
                profile_picture_content_type
            )
        )

        profile_picture_file_path = (
            os.path.join(
                settings.PROFILE_PICTURE_DIR,
                profile_picture_filename,
            )
        )

        with open(
            profile_picture_file_path,
            "wb"
        ) as buffer:
            buffer.write(
                profile_picture_content
            )

    new_user = User(

        full_name=full_name,

        email=email,

        hashed_password=hashed_password,

        resume_filename=resume_filename,

        profile_picture_filename=profile_picture_filename
    )

    db.add(new_user)

    try:
        db.commit()
    except Exception:
        db.rollback()

        for file_path in (
            resume_file_path,
            profile_picture_file_path,
        ):
            if (
                file_path
                and os.path.isfile(file_path)
            ):
                os.remove(file_path)

        raise

    db.refresh(new_user)

    return new_user