"""
transaction_monitor.py

Unsupervised anomaly detection for financial transactions using
Isolation Forest. Learns what "normal" transaction behavior looks like
from historical data, then scores new transactions (single or batch)
by how much they deviate from that learned normal.

Built against a PaySim-style schema:
    step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    nameDest, oldbalanceDest, newbalanceDest

If your actual dataset's column names differ, update COLUMN_MAP below —
the rest of the module reads through that map rather than hardcoding
column names everywhere, so it's a one-spot fix.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "models/isolation_forest.joblib"
SCALER_PATH = "models/scaler.joblib"
ENCODER_PATH = "models/type_encoder.joblib"

# Map our internal feature names to your actual CSV column names.
# Change the right-hand side values if your dataset uses different headers.
COLUMN_MAP = {
    "amount": "amount",
    "type": "type",
    "old_balance_orig": "oldbalanceOrg",
    "new_balance_orig": "newbalanceOrig",
    "old_balance_dest": "oldbalanceDest",
    "new_balance_dest": "newbalanceDest",
    "step": "step",
}


def _engineer_features(df: pd.DataFrame, type_categories=None):
    """
    Turns raw transaction columns into numeric features the model can
    learn from. Returns (feature_dataframe, type_categories_used).

    Engineered features (not just raw columns) because raw balances
    alone don't capture what's actually unusual — the *change* in
    balance relative to the transaction amount is what reveals
    inconsistencies (e.g. a transfer that doesn't actually debit the
    sender's account by the stated amount is a classic fraud signature).
    """

    cols = COLUMN_MAP

    features = pd.DataFrame(index=df.index)

    features["amount"] = df[cols["amount"]].astype(float)

    orig_old = df[cols["old_balance_orig"]].astype(float)
    orig_new = df[cols["new_balance_orig"]].astype(float)
    dest_old = df[cols["old_balance_dest"]].astype(float)
    dest_new = df[cols["new_balance_dest"]].astype(float)

    features["orig_balance_delta"] = orig_old - orig_new
    features["dest_balance_delta"] = dest_new - dest_old

    # Discrepancy between the stated amount and the actual balance change.
    # Large discrepancies are a strong anomaly signal in transaction data.
    features["orig_amount_mismatch"] = (
        features["orig_balance_delta"] - features["amount"]
    ).abs()

    # Did the sender's account get drained to (near) zero? Common in
    # account-takeover / mule-account patterns.
    features["orig_drained"] = (orig_new <= 0.01).astype(int)

    if cols["step"] in df.columns:
        features["step"] = df[cols["step"]].astype(float)
    else:
        features["step"] = 0.0

    # One-hot encode transaction type
    type_col = df[cols["type"]].astype(str)

    if type_categories is None:
        type_categories = sorted(type_col.unique().tolist())

    for cat in type_categories:
        features[f"type_{cat}"] = (type_col == cat).astype(int)

    return features, type_categories


def train_model(df: pd.DataFrame, contamination=0.02, random_state=42):
    """
    Trains an Isolation Forest on historical transaction data.

    contamination: expected proportion of anomalies in the data.
    2% is a reasonable starting default for transaction fraud —
    adjust based on what you know about your dataset (e.g. PaySim's
    documented fraud rate is roughly 0.1%, real card fraud is often
    even lower — tune this once you have your real dataset in hand).

    Returns a dict with the fitted model, scaler, and feature metadata
    needed to score new transactions later.
    """

    features, type_categories = _engineer_features(df)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features.values)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(scaled)

    artifact = {
        "model": model,
        "scaler": scaler,
        "type_categories": type_categories,
        "feature_columns": list(features.columns),
    }

    os.makedirs("models", exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)

    return artifact


def load_model():
    """Loads a previously trained model artifact, or None if none exists."""

    if not os.path.exists(MODEL_PATH):
        return None

    return joblib.load(MODEL_PATH)


def score_batch(artifact, df: pd.DataFrame):
    """
    Scores every row in df against the trained model.

    Returns the original dataframe with two new columns:
        anomaly_score  -> raw Isolation Forest decision function value
                           (lower = more anomalous)
        is_flagged     -> True if the model's predict() called it an outlier

    Also returns a normalized 0-100 "risk score" per row for display,
    where 100 = most anomalous in this batch.
    """

    features, _ = _engineer_features(df, type_categories=artifact["type_categories"])

    # Align columns in case some type categories weren't present in this batch
    for col in artifact["feature_columns"]:
        if col not in features.columns:
            features[col] = 0
    features = features[artifact["feature_columns"]]

    scaled = artifact["scaler"].transform(features.values)

    raw_scores = artifact["model"].decision_function(scaled)
    predictions = artifact["model"].predict(scaled)  # -1 = anomaly, 1 = normal

    result = df.copy()
    result["anomaly_score"] = raw_scores
    result["is_flagged"] = predictions == -1

    # Normalize raw scores to an intuitive 0-100 scale for THIS batch only.
    # Lower raw score = more anomalous, so we invert it.
    min_s, max_s = raw_scores.min(), raw_scores.max()
    span = max_s - min_s if max_s != min_s else 1.0
    result["risk_score"] = (
        (1 - (raw_scores - min_s) / span) * 100
    ).round(1)

    return result.sort_values("risk_score", ascending=False)


def score_transaction(artifact, transaction: dict):
    """
    Scores a single new transaction (dict of raw field values matching
    COLUMN_MAP's right-hand side names) against the trained model.

    Returns a dict with the anomaly score, flagged status, a 0-100 risk
    score, and a breakdown of which engineered features were most
    unusual relative to the training data's feature distribution
    (so the UI can explain *why* something was flagged, not just that
    it was).
    """

    row_df = pd.DataFrame([transaction])

    features, _ = _engineer_features(row_df, type_categories=artifact["type_categories"])

    for col in artifact["feature_columns"]:
        if col not in features.columns:
            features[col] = 0
    features = features[artifact["feature_columns"]]

    scaled = artifact["scaler"].transform(features.values)

    raw_score = artifact["model"].decision_function(scaled)[0]
    prediction = artifact["model"].predict(scaled)[0]

    # Compute per-feature z-scores (using the scaler's learned mean/std)
    # so we can explain which inputs were most out-of-distribution.
    means = artifact["scaler"].mean_
    stds = artifact["scaler"].scale_
    raw_values = features.values[0]

    z_scores = np.abs((raw_values - means) / np.where(stds == 0, 1, stds))

    contributors = sorted(
        zip(artifact["feature_columns"], z_scores),
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    return {
        "anomaly_score": float(raw_score),
        "is_flagged": bool(prediction == -1),
        "top_contributors": [
            {"feature": name, "z_score": round(float(z), 2)}
            for name, z in contributors
        ],
    }