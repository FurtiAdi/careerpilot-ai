from app.skills.scorer import calculate_match_score


def test_full_match():
    result = calculate_match_score(
        candidate_skills=["Python", "FastAPI", "Docker"],
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
    )

    assert result["match_score"] == 100

    assert set(
        result["matched_required_skills"]
    ) == {
        "python",
        "fastapi",
    }

    assert set(
        result["matched_preferred_skills"]
    ) == {
        "docker",
    }


def test_partial_required_match():
    result = calculate_match_score(
        candidate_skills=["Python"],
        required_skills=["Python", "FastAPI"],
        preferred_skills=[],
    )

    assert result["match_score"] == 40

    assert result["matched_required_skills"] == [
        "python"
    ]

    assert result["missing_required_skills"] == [
        "fastapi"
    ]


def test_only_preferred_skills_match():
    result = calculate_match_score(
        candidate_skills=["Docker"],
        required_skills=["Python"],
        preferred_skills=["Docker"],
    )

    assert result["match_score"] == 20

    assert result["matched_required_skills"] == []

    assert result["matched_preferred_skills"] == [
        "docker"
    ]


def test_no_skills_match():
    result = calculate_match_score(
        candidate_skills=["Java"],
        required_skills=["Python"],
        preferred_skills=["Docker"],
    )

    assert result["match_score"] == 0

    assert result["missing_required_skills"] == [
        "python"
    ]

    assert result["missing_preferred_skills"] == [
        "docker"
    ]


def test_no_required_skills():
    result = calculate_match_score(
        candidate_skills=["Docker"],
        required_skills=[],
        preferred_skills=["Docker"],
    )

    assert result["match_score"] == 20
    assert result["preferred_score"] == 100