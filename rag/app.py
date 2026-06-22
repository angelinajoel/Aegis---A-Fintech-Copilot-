import time
import streamlit as st

from rag.rag_pipeline import generate_response
from rag.graph_viz import render_subgraph_svg

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
        ["Risk Chat", "Pipeline Trace", "System Overview"],
        index=["Risk Chat", "Pipeline Trace", "System Overview"].index(st.session_state.page),
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

        svg = render_subgraph_svg(subgraph)
        if svg:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-label'>Knowledge graph — traversed subgraph</div>", unsafe_allow_html=True)
            st.markdown(svg, unsafe_allow_html=True)
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