def classify_query(query):

    query = query.lower()

    if "kyc" in query:
        return "KYC"

    if "aml" in query:
        return "AML"

    if "fraud" in query:
        return "Fraud Detection"

    if "compliance" in query:
        return "Compliance"

    if "risk" in query:
        return "Risk Management"

    return "General Intelligence"