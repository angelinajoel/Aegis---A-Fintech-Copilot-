import streamlit as st

from rag.rag_pipeline import generate_response

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Aegis AI",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------
# CHAT HISTORY
# ---------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------
# LOAD CSS
# ---------------------------------

with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ---------------------------------
# SIDEBAR
# ---------------------------------

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/2092/2092063.png",
        width=120
    )

    st.title("Aegis AI")

    st.markdown("---")

    st.markdown("### Features")

    st.markdown("""
    ✅ Hybrid RAG
    ✅ GraphRAG
    ✅ ChromaDB
    ✅ Groq LLM
    ✅ Risk Intelligence
    ✅ Fraud Analysis
    ✅ Compliance Analysis
    ✅ Knowledge Graph
    """)

    st.markdown("---")

    st.markdown("### System Status")

    st.success("LLM Connected")
    st.success("Vector DB Active")
    st.success("Graph Engine Running")

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Compliance PDF",git status
        type=["pdf"]
    )

    if uploaded_file:
        st.success("PDF Uploaded")

    st.markdown("---")

    st.subheader("Recent Queries")

    for item in reversed(
        st.session_state.chat_history[-5:]
    ):

        st.write(
            f"🧑 {item['query']}"
        )

# ---------------------------------
# MAIN TITLE
# ---------------------------------

st.markdown(
    """
    <div class='title-glow'>
        🛡️ Aegis AI
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<center>AI-Powered Financial Risk Intelligence Platform</center>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------
# INPUT
# ---------------------------------

query = st.text_input(
    "Ask a financial risk or compliance question"
)

# ---------------------------------
# ANALYZE BUTTON
# ---------------------------------

if st.button("Analyze Risk"):

    if query:

        with st.spinner(
            "Running Hybrid RAG + GraphRAG Pipeline..."
        ):

            result = generate_response(query)

        response = result["answer"]

        evidence = result["evidence"]

        risk_score = result["risk_score"]

        risk_level = result["risk_level"]

        category = result["category"]

        confidence = min(
            75 + len(evidence) * 5,
            95
        )

        st.session_state.chat_history.append(
            {
                "query": query,
                "answer": response
            }
        )

        # ---------------------------------
        # ANSWER
        # ---------------------------------

        st.markdown("## 🛡️ Aegis Analysis")

        st.markdown(response)

        # ---------------------------------
        # METRICS
        # ---------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Confidence",
                f"{confidence}%"
            )

        with col2:
            st.metric(
                "Sources",
                len(evidence)
            )

        with col3:
            st.metric(
                "Risk Score",
                risk_score
            )

        with col4:
            st.metric(
                "Category",
                category
            )

        st.info(
            f"Risk Level: {risk_level}"
        )

        # ---------------------------------
        # EVIDENCE PANEL
        # ---------------------------------

        with st.expander(
            "📚 Sources Used By Aegis"
        ):

            st.markdown(
                """
                The following knowledge sources
                were retrieved and used to
                generate the answer.
                """
            )

            for source in evidence:

                st.markdown("---")

                st.write(source)

# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.caption(
    "Built with ChromaDB + Hybrid RAG + GraphRAG + Groq LLM"
)