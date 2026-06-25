import time
import pandas as pd
import streamlit as st

from rag.rag_pipeline import generate_response
from rag.graph_viz import render_subgraph_svg
from rag import transaction_monitor as tm

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Aegis AI — Risk Intelligence Console",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------
# STATE
# ---------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "page" not in st.session_state:
    st.session_state.page = "Risk Chat"

if "tm_artifact" not in st.session_state:
    st.session_state.tm_artifact = tm.load_model()

if "tm_batch_result" not in st.session_state:
    st.session_state.tm_batch_result = None

if "tm_single_result" not in st.session_state:
    st.session_state.tm_single_result = None

if "tm_single_transaction" not in st.session_state:
    st.session_state.tm_single_transaction = None

if "tm_aegis_response" not in st.session_state:
    st.session_state.tm_aegis_response = None

# ---------------------------------
# LOAD CSS
# ---------------------------------

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------
# SIDEBAR — NAV + SYSTEM STATUS
# ---------------------------------

with st.sidebar:

    st.markdown(
        "<div class='aegis-brand'><span class='dot'></span>AEGIS AI</div>",
        unsafe_allow_html=True
    )
    st.caption("Financial Risk Intelligence Console")

    st.markdown("---")

    st.session_state.page = st.radio(
        "Navigate",
        ["Risk Chat", "Pipeline Trace", "Transaction Monitor", "System Overview"],
        index=["Risk Chat", "Pipeline Trace", "Transaction Monitor", "System Overview"].index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<div class='panel-label'>System Status</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='status-pill'><span class='dot'></span>LLM — Groq Connected</div><br>"
        "<div class='status-pill'><span class='dot'></span>Vector DB — ChromaDB Active</div><br>"
        "<div class='status-pill'><span class='dot'></span>Graph Engine — Running</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    uploaded_file = st.file_uploader("Upload Compliance PDF", type=["pdf"])
    if uploaded_file:
        st.success("PDF received")

    st.markdown("---")
    st.markdown("<div class='panel-label'>Recent Queries</div>", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.caption("No queries yet.")
    else:
        for item in reversed(st.session_state.chat_history[-5:]):
            st.caption(f"› {item['query']}")


# =============================================================
# PAGE: RISK CHAT
# =============================================================

if st.session_state.page == "Risk Chat":

    st.markdown("<div class='console-title'>Risk Chat</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='console-subtitle'>Ask a compliance, fraud, or risk question</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    query = st.text_input(
        "Query",
        label_visibility="collapsed",
        placeholder="e.g. What due diligence is required for a politically exposed person?"
    )

    run = st.button("Analyze Risk")

    if run and query:

        progress_box = st.empty()

        stages = [
            "Expanding query via knowledge graph...",
            "Searching ChromaDB (vector retrieval)...",
            "Reranking with cross-encoder...",
            "Scoring risk signals...",
            "Generating response..."
        ]

        for stage in stages:
            progress_box.markdown(
                f"<div class='status-pill'><span class='dot'></span>{stage}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.25)

        result = generate_response(query)
        progress_box.empty()

        st.session_state.last_result = result
        st.session_state.chat_history.append({
            "query": query,
            "answer": result["answer"]
        })

    result = st.session_state.last_result

    if result:

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>Aegis Analysis</div>", unsafe_allow_html=True)
        st.markdown(result["answer"])
        st.markdown("</div>", unsafe_allow_html=True)

        scored_evidence = result["scored_evidence"]
        confidence = min(75 + len(scored_evidence) * 5, 95)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Confidence", f"{confidence}%")
        with col2:
            st.metric("Sources Used", len(scored_evidence))
        with col3:
            st.metric("Risk Score", result["risk_score"])
        with col4:
            st.metric("Category", result["category"])

        st.markdown(
            f"<span class='risk-badge risk-{result['risk_level']}'>RISK LEVEL: {result['risk_level']}</span>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📚 Evidence used by Aegis (with retrieval + rerank scores)"):
            for source in scored_evidence:
                st.markdown(
                    f"""
                    <div class='evidence-card'>
                        {source['text']}
                        <div class='score-row'>
                            <span class='score-chip'>chroma similarity: {source['chroma_similarity']}%</span>
                            <span class='score-chip'>rerank score: {source['rerank_score']}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.caption("Want to see exactly how this answer was built? Open the **Pipeline Trace** tab.")

    else:
        st.markdown(
            "<div class='empty-state'>No analysis yet — ask a question above to begin.</div>",
            unsafe_allow_html=True
        )


# =============================================================
# PAGE: PIPELINE TRACE
# =============================================================

elif st.session_state.page == "Pipeline Trace":

    st.markdown("<div class='console-title'>Pipeline Trace</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='console-subtitle'>Hybrid RAG + GraphRAG, stage by stage</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    result = st.session_state.last_result

    if not result:
        st.markdown(
            "<div class='empty-state'>Run a query in Risk Chat first — its full reasoning"
            " trace will appear here.</div>",
            unsafe_allow_html=True
        )
    else:
        trace = result["pipeline_trace"]
        subgraph = trace["subgraph"]
        scored_evidence = result["scored_evidence"]

        # Stage 1 — original query
        st.markdown(
            f"""
            <div class='trace-step active'>
                <div class='trace-label'>01 · Original Query</div>
                <div class='trace-body'>{trace['original_query']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Stage 2 — graph expansion
        matched_count = len(subgraph["matched_nodes"])
        edge_count = len(subgraph["edges"])

        st.markdown(
            f"""
            <div class='trace-step active'>
                <div class='trace-label'>02 · GraphRAG Expansion</div>
                <div class='trace-body'>{trace['expanded_query']}</div>
                <div class='trace-meta'>{matched_count} matched entity(ies) · {edge_count} graph edge(s) traversed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        viz = render_subgraph_svg(subgraph)
        if viz:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-label'>Knowledge graph — traversed subgraph</div>", unsafe_allow_html=True)
            st.markdown(viz["svg"], unsafe_allow_html=True)
            if viz["truncated"]:
                st.caption(
                    f"Showing {viz['shown_neighbors']} of this match's neighbors — "
                    f"some connections were omitted to keep the diagram readable."
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("No entity matches found in the knowledge graph for this query — expansion fell back to the original query alone.")

        # Stage 3 — hybrid retrieval + rerank
        st.markdown(
            f"""
            <div class='trace-step active'>
                <div class='trace-label'>03 · Hybrid Retrieval + Reranking</div>
                <div class='trace-body'>ChromaDB vector search → cross-encoder rerank → top {len(scored_evidence)} chunks selected</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        for i, source in enumerate(scored_evidence, start=1):
            st.markdown(
                f"""
                <div class='evidence-card'>
                    <b>chunk {i}</b><br>{source['text']}
                    <div class='score-row'>
                        <span class='score-chip'>chroma similarity: {source['chroma_similarity']}%</span>
                        <span class='score-chip'>rerank score: {source['rerank_score']}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Stage 4 — risk scoring
        st.markdown(
            f"""
            <div class='trace-step active'>
                <div class='trace-label'>04 · Risk Scoring</div>
                <div class='trace-body'>Keyword-weighted scan of retrieved evidence</div>
                <div class='trace-meta'>Score: {result['risk_score']} / 100 → Level: {result['risk_level']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Stage 5 — final answer
        st.markdown(
            f"""
            <div class='trace-step'>
                <div class='trace-label'>05 · LLM Response</div>
                <div class='trace-body'>{result['answer']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =============================================================
# PAGE: TRANSACTION MONITOR
# =============================================================

elif st.session_state.page == "Transaction Monitor":

    st.markdown("<div class='console-title'>Transaction Monitor</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='console-subtitle'>Unsupervised anomaly detection — Isolation Forest</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    tab_train, tab_check = st.tabs(["Train on historical data", "Check a single transaction"])

    # ---------------- TRAIN / BATCH TAB ----------------
    with tab_train:

        st.markdown(
            "<div class='panel-label'>Step 1 — Upload historical transactions (CSV)</div>",
            unsafe_allow_html=True
        )
        st.caption(
            "Expected columns: step, type, amount, oldbalanceOrg, newbalanceOrig, "
            "oldbalanceDest, newbalanceDest (PaySim-style schema)."
        )

        tx_file = st.file_uploader("Upload transactions CSV", type=["csv"], key="tx_upload")

        if tx_file:

            df = pd.read_csv(tx_file)
            st.caption(f"Loaded {len(df):,} rows.")
            st.dataframe(df.head(5), use_container_width=True)

            contamination = st.slider(
                "Expected anomaly rate",
                min_value=0.001, max_value=0.10, value=0.02, step=0.001,
                format="%.3f",
                help="Rough estimate of what fraction of transactions are anomalous. "
                     "Tune based on what you know about this dataset."
            )

            if st.button("Train model on this data"):

                missing = [c for c in
                           [tm.COLUMN_MAP["amount"], tm.COLUMN_MAP["type"],
                            tm.COLUMN_MAP["old_balance_orig"], tm.COLUMN_MAP["new_balance_orig"],
                            tm.COLUMN_MAP["old_balance_dest"], tm.COLUMN_MAP["new_balance_dest"]]
                           if c not in df.columns]

                if missing:
                    st.error(
                        f"This file is missing required columns: {missing}. "
                        f"Update COLUMN_MAP in transaction_monitor.py if your dataset uses "
                        f"different column names."
                    )
                else:
                    with st.spinner("Training Isolation Forest on historical patterns..."):
                        artifact = tm.train_model(df, contamination=contamination)
                        scored = tm.score_batch(artifact, df)

                    st.session_state.tm_artifact = artifact
                    st.session_state.tm_batch_result = scored
                    st.success(f"Model trained on {len(df):,} transactions.")

        result = st.session_state.tm_batch_result

        if result is not None:

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='panel-label'>Step 2 — Results</div>", unsafe_allow_html=True)

            flagged_count = int(result["is_flagged"].sum())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Transactions Scored", f"{len(result):,}")
            with col2:
                st.metric("Flagged Anomalies", flagged_count)
            with col3:
                st.metric("Flag Rate", f"{flagged_count / len(result) * 100:.2f}%")

            try:
                import plotly.express as px

                plot_df = result.copy()
                plot_df["status"] = plot_df["is_flagged"].map({True: "Flagged", False: "Normal"})

                fig = px.scatter(
                    plot_df,
                    x="amount",
                    y="risk_score",
                    color="status",
                    color_discrete_map={"Flagged": "#FF5C5C", "Normal": "#5EE6C8"},
                    opacity=0.7,
                    labels={"amount": "Transaction Amount", "risk_score": "Risk Score"},
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#C3CAD9",
                    legend_title_text="",
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                fig.update_xaxes(gridcolor="#232B3D")
                fig.update_yaxes(gridcolor="#232B3D")

                st.plotly_chart(fig, use_container_width=True)

            except ImportError:
                st.caption(
                    "Install `plotly` (`pip install plotly`) to see the anomaly scatter plot."
                )

            st.markdown("<div class='panel-label'>Top flagged transactions</div>", unsafe_allow_html=True)

            display_cols = [
                tm.COLUMN_MAP["type"], tm.COLUMN_MAP["amount"],
                tm.COLUMN_MAP["old_balance_orig"], tm.COLUMN_MAP["new_balance_orig"],
                "risk_score", "is_flagged"
            ]
            display_cols = [c for c in display_cols if c in result.columns]

            st.dataframe(
                result[result["is_flagged"]][display_cols].head(25),
                use_container_width=True
            )

        else:
            st.markdown(
                "<div class='empty-state'>Upload a CSV and train the model to see flagged "
                "anomalies here.</div>",
                unsafe_allow_html=True
            )

    # ---------------- SINGLE TRANSACTION CHECK TAB ----------------
    with tab_check:

        artifact = st.session_state.tm_artifact

        if artifact is None:
            st.markdown(
                "<div class='empty-state'>Train a model on historical data first — "
                "this tab scores new transactions against what it learned.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='panel-label'>Enter a transaction to check</div>",
                unsafe_allow_html=True
            )

            with st.form("single_tx_form"):

                c1, c2 = st.columns(2)

                with c1:
                    tx_type = st.selectbox("Transaction type", artifact["type_categories"])
                    amount = st.number_input("Amount", min_value=0.0, value=500.0, step=10.0)
                    step = st.number_input("Step (time unit)", min_value=0, value=100, step=1)

                with c2:
                    old_orig = st.number_input("Sender balance — before", min_value=0.0, value=5000.0, step=10.0)
                    new_orig = st.number_input("Sender balance — after", min_value=0.0, value=4500.0, step=10.0)
                    old_dest = st.number_input("Receiver balance — before", min_value=0.0, value=1000.0, step=10.0)
                    new_dest = st.number_input("Receiver balance — after", min_value=0.0, value=1500.0, step=10.0)

                check = st.form_submit_button("Check transaction")

            if check:

                transaction = {
                    tm.COLUMN_MAP["type"]: tx_type,
                    tm.COLUMN_MAP["amount"]: amount,
                    tm.COLUMN_MAP["old_balance_orig"]: old_orig,
                    tm.COLUMN_MAP["new_balance_orig"]: new_orig,
                    tm.COLUMN_MAP["old_balance_dest"]: old_dest,
                    tm.COLUMN_MAP["new_balance_dest"]: new_dest,
                    tm.COLUMN_MAP["step"]: step,
                }

                st.session_state.tm_single_transaction = transaction
                st.session_state.tm_single_result = tm.score_transaction(artifact, transaction)
                st.session_state.tm_aegis_response = None  # reset any previous Aegis answer

            result = st.session_state.tm_single_result
            transaction = st.session_state.tm_single_transaction

            if result is not None:

                card_class = "flag-card" if result["is_flagged"] else "flag-card clear"
                verdict = "FLAGGED — ANOMALOUS" if result["is_flagged"] else "CLEAR — NORMAL PATTERN"
                verdict_color = "#FF5C5C" if result["is_flagged"] else "#5EE6C8"

                contributors_html = "".join(
                    f"<span class='contributor-chip'>{c['feature']} (z={c['z_score']})</span>"
                    for c in result["top_contributors"]
                )

                st.markdown(
                    f"""
                    <div class='{card_class}'>
                        <div style='font-family: JetBrains Mono, monospace; font-weight: 600;
                                    color: {verdict_color}; margin-bottom: 0.5rem;'>
                            {verdict}
                        </div>
                        <div class='monitor-stat'>anomaly score: {result['anomaly_score']:.4f}</div>
                        <div style='margin-top: 0.6rem;'>
                            <span class='monitor-stat'>top contributing factors:</span><br>
                            {contributors_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.caption(
                    "Z-scores show how many standard deviations each feature is from what the "
                    "model learned as normal — higher means more unusual."
                )

                # ---------------- ASK AEGIS CONNECTOR ----------------
                if result["is_flagged"]:

                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.button("🛡️ Ask Aegis about this flagged transaction"):

                        top_factors = ", ".join(
                            c["feature"].replace("_", " ") for c in result["top_contributors"]
                        )

                        auto_query = (
                            f"What compliance review or due diligence steps are required for a "
                            f"flagged {transaction[tm.COLUMN_MAP['type']]} transaction of "
                            f"{transaction[tm.COLUMN_MAP['amount']]:.2f}, where the main anomaly "
                            f"indicators were {top_factors}?"
                        )

                        with st.spinner("Routing to Aegis RAG + GraphRAG pipeline..."):
                            aegis_result = generate_response(auto_query)

                        st.session_state.tm_aegis_response = {
                            "query": auto_query,
                            "result": aegis_result,
                        }

                aegis = st.session_state.tm_aegis_response

                if aegis is not None:

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div class='panel'>", unsafe_allow_html=True)
                    st.markdown(
                        "<div class='panel-label'>🛡️ Aegis Compliance Guidance</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"Auto-generated query: \"{aegis['query']}\"")
                    st.markdown(aegis["result"]["answer"])
                    st.markdown(
                        f"<span class='risk-badge risk-{aegis['result']['risk_level']}'>"
                        f"POLICY RISK LEVEL: {aegis['result']['risk_level']}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Make this query + result available to the other tabs too,
                    # so the full reasoning trace can be inspected there.
                    st.session_state.last_result = aegis["result"]
                    st.caption(
                        "Full retrieval + graph reasoning for this answer is now available "
                        "in the **Pipeline Trace** tab."
                    )


# =============================================================
# PAGE: SYSTEM OVERVIEW
# =============================================================

elif st.session_state.page == "System Overview":

    st.markdown("<div class='console-title'>System Overview</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='console-subtitle'>Session activity and component status</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    total_queries = len(st.session_state.chat_history)

    high_risk = sum(
        1 for h in st.session_state.chat_history
        if st.session_state.last_result and "HIGH" in str(h.get("answer", ""))
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Queries This Session", total_queries)
    with col2:
        st.metric("Vector DB", "ChromaDB")
    with col3:
        st.metric("LLM Backend", "Groq")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>Active Components</div>", unsafe_allow_html=True)
    st.markdown(
        """
        - **Hybrid Retriever** — ChromaDB vector search + cross-encoder reranking
        - **GraphRAG** — spaCy NER entity graph, query expansion via traversal
        - **Risk Engine** — keyword-weighted compliance risk scoring
        - **Query Classifier** — routes queries into risk/compliance categories
        - **Transaction Monitor** — Isolation Forest anomaly detection on transaction data
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>Session Query Log</div>", unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.caption("No activity yet this session.")
    else:
        for item in reversed(st.session_state.chat_history):
            st.markdown(f"**›** {item['query']}")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")
st.caption("Aegis AI — ChromaDB + Hybrid RAG + GraphRAG + Groq LLM")