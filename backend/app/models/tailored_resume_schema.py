from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResumeContact(StrictSchema):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)


class ResumeExperience(StrictSchema):
    employer: str = Field(min_length=1)
    title: str = Field(min_length=1)
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = Field(default_factory=list)


class ResumeEducation(StrictSchema):
    institution: str = Field(min_length=1)
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    details: list[str] = Field(default_factory=list)


class ResumeProject(StrictSchema):
    name: str = Field(min_length=1)
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class ResumeOptionalSection(StrictSchema):
    heading: str = Field(min_length=1)
    items: list[str] = Field(default_factory=list)


class TailoredResumeContent(StrictSchema):
    contact: ResumeContact
    summary: str | None = None
    experience: list[ResumeExperience] = Field(
        default_factory=list
    )
    education: list[ResumeEducation] = Field(
        default_factory=list
    )
    skills: list[str] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(
        default_factory=list
    )
    optional_sections: list[ResumeOptionalSection] = Field(
        default_factory=list
    )


class TailoredResumeAIResponse(StrictSchema):
    content: TailoredResumeContent
    emphasized_items: list[str] = Field(
        default_factory=list
    )
    reordered_items: list[str] = Field(
        default_factory=list
    )


class TailoredResumeGenerateRequest(StrictSchema):
    analysis_id: int = Field(gt=0)
    source_content: TailoredResumeContent


class TailoredResumeResponse(StrictSchema):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    user_id: int
    source_analysis_id: int
    source_resume_filename: str
    version_group_id: str
    version_number: int
    status: Literal["draft", "saved"]
    content: TailoredResumeContent
    emphasized_items: list[str]
    reordered_items: list[str]
    match_snapshot: dict[str, object]
    created_at: datetime
    updated_at: datetime