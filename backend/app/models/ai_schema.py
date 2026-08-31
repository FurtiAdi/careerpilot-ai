from pydantic import BaseModel, Field


class AIAnalysisResponse(BaseModel):
    summary: str = Field(min_length=1)

    strengths: list[str] = Field(
        default_factory=list
    )

    missing_requirements: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )