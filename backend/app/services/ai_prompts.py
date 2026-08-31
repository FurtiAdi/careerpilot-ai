AI_ANALYSIS_MODEL = "gpt-4.1-mini"


AI_ANALYSIS_SYSTEM_PROMPT = (
    "You are an AI career assistant. "
    "Provide concise, practical career advice."
)


def format_skills(skills: list[str]) -> str:
    if not skills:
        return "None"

    return ", ".join(skills)


def build_analysis_prompt(
    match_score: int,
    matched_required_skills: list[str],
    missing_required_skills: list[str],
    matched_preferred_skills: list[str],
    missing_preferred_skills: list[str],
) -> str:
    return f"""
A deterministic job-match calculation has already been completed.

Do not change the match score or invent additional skill gaps.
Use the provided result to explain the candidate's fit and give
concise, practical recommendations.

Match Score: {match_score}%

Matched Required Skills:
{format_skills(matched_required_skills)}

Missing Required Skills:
{format_skills(missing_required_skills)}

Matched Preferred Skills:
{format_skills(matched_preferred_skills)}

Missing Preferred Skills:
{format_skills(missing_preferred_skills)}
"""