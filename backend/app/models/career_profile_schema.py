from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CareerProfileContact(StrictSchema):
    full_name: str | None = None
    headline: str | None = Field(
        default=None,
        description=(
            "A professional headline only when explicitly "
            "supported by the source CV."
        ),
    )
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)


class CareerProfileExperience(StrictSchema):
    title: str = Field(min_length=1)
    employer: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = Field(default_factory=list)


class CareerProfileEducation(StrictSchema):
    institution: str = Field(min_length=1)
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    details: list[str] = Field(default_factory=list)


class CareerProfileCertificate(StrictSchema):
    name: str = Field(min_length=1)
    issuer: str | None = None
    date: str | None = None
    details: list[str] = Field(default_factory=list)


class CareerProfileContent(StrictSchema):
    contact: CareerProfileContact
    experience: list[CareerProfileExperience] = Field(
        default_factory=list,
    )
    education: list[CareerProfileEducation] = Field(
        default_factory=list,
    )
    skills: list[str] = Field(default_factory=list)
    certificates: list[CareerProfileCertificate] = Field(
        default_factory=list,
    )


class CareerProfileExtractRequest(StrictSchema):
    source_resume_id: int = Field(gt=0)

    
class CareerProfileResponse(StrictSchema):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    user_id: int
    source_resume_id: int
    status: Literal["draft", "reviewed"]
    content: CareerProfileContent
    created_at: datetime
    updated_at: datetime