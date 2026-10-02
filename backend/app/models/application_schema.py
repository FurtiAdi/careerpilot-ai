from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


ApplicationStatus = Literal[
    "saved",
    "applied",
    "screening",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
]


class StrictSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ApplicationCreateRequest(StrictSchema):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    status: ApplicationStatus = "saved"

    job_url: str | None = Field(
        default=None,
        max_length=2048,
    )
    job_description: str | None = None

    applied_at: date | None = None
    next_action_date: date | None = None
    notes: str | None = None

    analysis_id: int | None = Field(default=None, gt=0)
    tailored_resume_id: int | None = Field(
        default=None,
        gt=0,
    )
    cover_letter_id: int | None = Field(
        default=None,
        gt=0,
    )


class ApplicationUpdateRequest(StrictSchema):
    company: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    role: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    status: ApplicationStatus | None = None

    job_url: str | None = Field(
        default=None,
        max_length=2048,
    )
    job_description: str | None = None

    applied_at: date | None = None
    next_action_date: date | None = None
    notes: str | None = None

    analysis_id: int | None = Field(default=None, gt=0)
    tailored_resume_id: int | None = Field(
        default=None,
        gt=0,
    )
    cover_letter_id: int | None = Field(
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "At least one field must be provided."
            )

        return self


class ApplicationResponse(StrictSchema):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    user_id: int
    company: str
    role: str
    status: ApplicationStatus

    job_url: str | None
    job_description: str | None

    applied_at: date | None
    next_action_date: date | None
    notes: str | None

    analysis_id: int | None
    tailored_resume_id: int | None
    cover_letter_id: int | None

    created_at: datetime
    updated_at: datetime


class ApplicationEventResponse(StrictSchema):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    application_id: int
    user_id: int
    event_type: Literal["status_changed"]
    previous_status: ApplicationStatus | None
    new_status: ApplicationStatus
    note: str | None
    created_at: datetime