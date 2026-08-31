import os
import shutil

from app.services.upload_filenames import (
    generate_profile_picture_filename,
)

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.analysis_model import Analysis
from app.models.user_model import User


def get_user_profile(
    current_user: User
):

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "resume_filename": current_user.resume_filename,
        "profile_picture_filename":
            current_user.profile_picture_filename
    }


def save_profile_picture(
    file: UploadFile,
    current_user: User,
    db: Session
):

    upload_dir = "uploads/profile_pictures"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    unique_filename = generate_profile_picture_filename(
        file
    )

    file_path = (
        f"{upload_dir}/{unique_filename}"
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    current_user.profile_picture_filename = (
        unique_filename
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "profile_picture_filename":
            unique_filename
    }


def get_profile_stats(
    current_user: User,
    db: Session
):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).all()

    total_analyses = len(analyses)

    average_score = 0

    if total_analyses > 0:

        average_score = round(
            sum(
                analysis.match_score
                for analysis in analyses
            ) / total_analyses
        )

    return {
        "total_analyses": total_analyses,
        "average_match_score":
            average_score,
        "resume_uploaded": bool(
            current_user.resume_filename
        )
    }