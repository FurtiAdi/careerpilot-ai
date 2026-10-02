from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CoverLetterContent(StrictSchema):
    opening: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    motivation: str = Field(min_length=1)
    closing: str = Field(min_length=1)


class CoverLetterAIResponse(StrictSchema):
    content: CoverLetterContent


class CoverLetterGenerateRequest(StrictSchema):
    analysis_id: int = Field(gt=0)
    source_resume_id: int = Field(gt=0)
    source_tailored_resume_id: int | None = Field(
        default=None,
        gt=0,
    )
    tone: Literal["professional", "warm", "concise"] = (
        "professional"
    )
    length: Literal["short", "standard"] = "standard"


class CoverLetterUpdateRequest(StrictSchema):
    content: CoverLetterContent | None = None
    status: Literal["draft", "saved"] | None = None

    @model_validator(mode="after")
    def require_change(self):
        if self.content is None and self.status is None:
            raise ValueError(
                "At least one field must be provided."
            )

        return self


class CoverLetterResponse(StrictSchema):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    user_id: int
    source_analysis_id: int
    source_resume_id: int
    source_tailored_resume_id: int | None
    version_group_id: str
    version_number: int
    status: Literal["draft", "saved"]
    tone: Literal["professional", "warm", "concise"]
    length: Literal["short", "standard"]
    content: CoverLetterContent
    created_at: datetime
    updated_at: datetime