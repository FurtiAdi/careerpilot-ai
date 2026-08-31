from app.skills.requirements import (
    classify_skill_requirements,
)


def test_all_skills_required_when_no_preferred_section():
    job_description = """
    We are looking for a developer with
    Python, FastAPI and Docker experience.
    """

    result = classify_skill_requirements(
        job_description
    )

    assert "python" in result.required
    assert "fastapi" in result.required
    assert "docker" in result.required

    assert result.preferred == []


def test_separates_required_and_preferred_skills():
    job_description = """
    Experience with Python and FastAPI is required.
    Nice to have: Docker and Kubernetes.
    """

    result = classify_skill_requirements(
        job_description
    )

    assert "python" in result.required
    assert "fastapi" in result.required

    assert "docker" in result.preferred
    assert "kubernetes" in result.preferred


def test_preferred_skills_are_not_required():
    job_description = """
    Python is required.
    Preferred skills: Docker and PostgreSQL.
    """

    result = classify_skill_requirements(
        job_description
    )

    assert "python" in result.required

    assert "docker" not in result.required
    assert "postgresql" not in result.required

    assert "docker" in result.preferred
    assert "postgresql" in result.preferred


def test_duplicate_skill_is_kept_as_required():
    job_description = """
    Python and Docker are required.
    Nice to have: Docker and Kubernetes.
    """

    result = classify_skill_requirements(
        job_description
    )

    assert "docker" in result.required
    assert "docker" not in result.preferred
    assert "kubernetes" in result.preferred


def test_empty_job_description():
    result = classify_skill_requirements("")

    assert result.required == []
    assert result.preferred == []