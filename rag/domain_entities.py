"""
domain_entities.py

Curated domain vocabulary for entity extraction in graphrag.py.

WHY THIS EXISTS:
spaCy's generic NER (PERSON, ORG, GPE, DATE, etc.) is trained to find
real-world named entities — people, companies, places. Compliance/AML
policy text is abstract domain prose ("risk-based due diligence is
important") with almost no real-world named entities for spaCy to latch
onto. Running NER on it returns close to nothing, which makes GraphRAG's
query expansion silently do nothing.

The fix: treat domain *concepts* as the entities instead. "KYC", "EDD",
"structuring", "false positives" are the actual nouns this knowledge
base's relationships are organized around — they're just not the kind
of entity generic NER looks for.

This list was derived directly from financial_knowledge_base.txt by
reading through it and extracting the recurring domain noun phrases,
grouped here by category purely for human readability/maintainability —
the categories themselves aren't used at runtime, all terms are matched
the same way.

TO EXTEND: add new phrases to the relevant list (or a new list) below.
Multi-word phrases are matched as whole units (e.g. "money laundering"
is one entity, not "money" + "laundering" separately) — see
extract_domain_entities() in graphrag.py for the matching logic.
"""

COMPLIANCE_TERMS = [
    "kyc", "know your customer",
    "aml", "anti-money laundering",
    "edd", "enhanced due diligence",
    "due diligence", "customer due diligence", "risk-based due diligence",
    "pep", "politically exposed persons", "politically exposed person",
    "customer identification",
    "compliance programs", "compliance policies",
    "regulated industries",
    "audit trails",
]

FRAUD_PATTERN_TERMS = [
    "money laundering", "terrorist financing",
    "placement", "layering", "integration",
    "structuring",
    "account takeover",
    "suspicious transaction monitoring",
    "fraud detection", "fraud patterns", "fraud cases",
    "identity theft",
    "false positives",
]

RISK_TERMS = [
    "risk score", "risk scores",
    "high risk", "low risk", "medium risk",
    "geographic risk assessment", "high-risk regions",
    "behavioral analytics",
    "transaction behavior", "transaction volume",
    "reporting thresholds",
]

ML_AI_TERMS = [
    "machine learning models", "machine learning",
    "anomaly detection", "anomalies",
    "explainable ai",
    "predictive analytics",
    "forecasting models",
    "risk models",
    "training data",
    "knowledge graphs", "graph analysis",
    "hybrid rag",
    "vector databases",
    "cross-encoder reranking", "reranking",
    "semantic search", "keyword search",
    "evidence-backed responses",
]

OPERATIONAL_TERMS = [
    "transaction monitoring systems", "transaction monitoring",
    "device information",
    "incident reports",
    "observability",
    "latency",
    "error rates",
    "application logs",
    "metrics",
    "capacity planning",
    "security controls",
    "risk management",
]

ALL_DOMAIN_TERMS = (
    COMPLIANCE_TERMS
    + FRAUD_PATTERN_TERMS
    + RISK_TERMS
    + ML_AI_TERMS
    + OPERATIONAL_TERMS
)

# Sort longest-first so multi-word phrases are matched before their
# shorter substrings (e.g. "money laundering" before "laundering" would
# match if "laundering" were ever added alone — longest-match-first
# avoids that class of bug entirely).
ALL_DOMAIN_TERMS = sorted(set(ALL_DOMAIN_TERMS), key=len, reverse=True)