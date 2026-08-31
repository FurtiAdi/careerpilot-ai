AI_ANALYSIS_MODEL = "gpt-4.1-mini"


AI_ANALYSIS_SYSTEM_PROMPT = (
    "You are an AI career assistant. "
    "Provide concise, practical career advice."
)


def build_analysis_prompt(
    job_description: str,
    candidate_skills: list[str],
) -> str:
    skills_text = ", ".join(candidate_skills)

    return f"""
Analyze the following job description and candidate skills.

Job Description:
{job_description}

Candidate Skills:
{skills_text}
"""