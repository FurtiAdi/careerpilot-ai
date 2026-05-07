from pydantic import BaseModel
from typing import List


class JobRequest(BaseModel):
    job_description: str
    candidate_skills: List[str]