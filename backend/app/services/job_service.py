from app.skills.extractor import (
    extract_skills_from_text
)


def extract_skills(
    job_description: str
):

    return extract_skills_from_text(
        job_description
    )

def calculate_match_score(job_skills, candidate_skills):

    matched_skills = []
    missing_skills = []

    normalized_candidate_skills = [
        skill.lower() for skill in candidate_skills
    ]

    for skill in job_skills:

        if skill in normalized_candidate_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if len(job_skills) == 0:
        score = 0
    else:
        score = int((len(matched_skills) / len(job_skills)) * 100)

    return {
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }