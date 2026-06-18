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

    for word in high_risk_keywords:

        if word in text:
            score += 20

    for word in medium_risk_keywords:

        if word in text:
            score += 10

    return min(score, 100)


def get_risk_level(score):

    if score >= 70:
        return "🔴 High"

    elif score >= 40:
        return "🟠 Medium"

    return "🟢 Low"