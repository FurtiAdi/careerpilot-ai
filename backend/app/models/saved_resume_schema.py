from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SavedResumeResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    original_filename: str
    created_at: datetime