from app.skills.normalizer import normalize_skills


REQUIRED_WEIGHT = 0.8
PREFERRED_WEIGHT = 0.2


def calculate_match_score(
    required_skills: list[str],
    preferred_skills: list[str],
    candidate_skills: list[str]
) -> dict:

    normalized_required = normalize_skills(
        required_skills
    )

    normalized_preferred = normalize_skills(
        preferred_skills
    )

    normalized_candidate = normalize_skills(
        candidate_skills
    )

    candidate_set = set(normalized_candidate)

    matched_required = [
        skill
        for skill in normalized_required
        if skill in candidate_set
    ]

    missing_required = [
        skill
        for skill in normalized_required
        if skill not in candidate_set
    ]

    matched_preferred = [
        skill
        for skill in normalized_preferred
        if skill in candidate_set
    ]

    missing_preferred = [
        skill
        for skill in normalized_preferred
        if skill not in candidate_set
    ]

    if normalized_required:

        required_score = (
            len(matched_required)
            / len(normalized_required)
        ) * 100

    else:

        required_score = 100

    if normalized_required:
        required_score = (
            len(matched_required)
            / len(normalized_required)
        ) * 100
    else:
        required_score = 0

    if normalized_preferred:
        preferred_score = (
            len(matched_preferred)
            / len(normalized_preferred)
        ) * 100
    else:
        preferred_score = 0

    if (
        not normalized_required
        and not normalized_preferred
    ):
        overall_score = 0
    else:
        overall_score = (
            required_score * REQUIRED_WEIGHT
            + preferred_score * PREFERRED_WEIGHT
        )

    return {
        "match_score": round(overall_score),

        "required_score": round(
            required_score
        ),

        "preferred_score": round(
            preferred_score
        ),

        "matched_required_skills":
            matched_required,

        "missing_required_skills":
            missing_required,

        "matched_preferred_skills":
            matched_preferred,

        "missing_preferred_skills":
            missing_preferred,

        "weights": {
            "required":
                REQUIRED_WEIGHT,

            "preferred":
                PREFERRED_WEIGHT
        }
    }