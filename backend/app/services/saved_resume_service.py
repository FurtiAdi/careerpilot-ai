from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.saved_resume_model import SavedResume
from app.services.upload_filenames import (
    generate_resume_filename,
)


def create_saved_resume(
    user_id: int,
    original_filename: str,
    content: bytes,
    db: Session,
) -> SavedResume:
    display_filename = Path(
        original_filename.replace("\\", "/")
    ).name or "resume.pdf"

    resume_directory = Path(settings.RESUME_DIR)
    resume_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage_filename = generate_resume_filename()
    resume_path = resume_directory / storage_filename
    resume_path.write_bytes(content)

    saved_resume = SavedResume(
        user_id=user_id,
        storage_filename=storage_filename,
        original_filename=display_filename,
    )

    try:
        db.add(saved_resume)
        db.commit()
    except Exception:
        db.rollback()

        if resume_path.is_file():
            resume_path.unlink()

        raise

    db.refresh(saved_resume)

    return saved_resume

def get_user_saved_resumes(
    user_id: int,
    db: Session,
) -> list[SavedResume]:
    return (
        db.query(SavedResume)
        .filter(SavedResume.user_id == user_id)
        .order_by(SavedResume.created_at.desc())
        .all()
    )


def get_user_saved_resume(
    saved_resume_id: int,
    user_id: int,
    db: Session,
) -> SavedResume | None:
    return db.query(SavedResume).filter(
        SavedResume.id == saved_resume_id,
        SavedResume.user_id == user_id,
    ).first()