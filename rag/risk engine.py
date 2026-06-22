def calculate_risk_score(text):

    text = text.lower()

    high_risk_keywords = [
        "fraud",
        "money laundering",
        "terrorist financing",
        "suspicious",
        "account takeover",
        "high risk"
    ]

    medium_risk_keywords = [
        "unusual",
        "alert",
        "anomaly",
        "review",
        "large transaction"
    ]

    score = 0

    for keyword in high_risk_keywords:
        if keyword in text:
            score += 20

    for keyword in medium_risk_keywords:
        if keyword in text:
            score += 10

    return min(score, 100)


def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    return "LOW"