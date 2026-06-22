def classify_query(query):

    query = query.lower()

    if "kyc" in query:
        return "KYC"

    elif "aml" in query:
        return "AML"

    elif "fraud" in query:
        return "Fraud Detection"

    elif "compliance" in query:
        return "Compliance"

    elif "risk" in query:
        return "Risk Management"

    return "General Intelligence"