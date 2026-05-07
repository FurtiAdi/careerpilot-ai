KNOWN_SKILLS = [
    "python",
    "fastapi",
    "react",
    "next.js",
    "javascript",
    "typescript",
    "sql",
    "postgresql",
    "docker",
    "aws",
    "git",
    "machine learning",
    "ai"
]


def extract_skills(job_description: str):

    found_skills = []

    lower_description = job_description.lower()

    for skill in KNOWN_SKILLS:

        if skill in lower_description:
            found_skills.append(skill)

    return found_skills