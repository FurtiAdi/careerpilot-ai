from app.skills.extractor import extract_skills_from_text


def test_extracts_basic_skills():
    text = """
    We are looking for a Python developer
    with FastAPI and Docker experience.
    """

    skills = extract_skills_from_text(text)

    assert "python" in skills
    assert "fastapi" in skills
    assert "docker" in skills


def test_extracts_aliases():
    text = """
    Experience with JS, Postgres and k8s is required.
    """

    skills = extract_skills_from_text(text)

    assert "javascript" in skills
    assert "postgresql" in skills
    assert "kubernetes" in skills


def test_does_not_match_ai_inside_unrelated_words():
    text = """
    The candidate should maintain reliable systems.
    """

    skills = extract_skills_from_text(text)

    assert "ai" not in skills


def test_extracts_ai_as_standalone_skill():
    text = """
    Experience with AI and machine learning is preferred.
    """

    skills = extract_skills_from_text(text)

    assert "artificial intelligence" in skills
    assert "machine learning" in skills
    

def test_does_not_return_duplicates():
    text = """
    Python developer with Python,
    python scripting and PYTHON experience.
    """

    skills = extract_skills_from_text(text)

    assert skills.count("python") == 1