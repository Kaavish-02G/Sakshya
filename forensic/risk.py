def risk_from_score(score: float | None) -> str:
    if score is None:
        return "INCONCLUSIVE"
    if score >= 0.70:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


def recommendation_for(score: float | None) -> str:
    if score is not None and score >= 0.40:
        return "FLAGGED FOR FURTHER FORENSIC REVIEW"
    return "No strong manipulation signal detected."
