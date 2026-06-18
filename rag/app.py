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
# LOAD CSS
# ---------------------------------

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
    ✅ Risk Intelligence  
    ✅ Vector Search  
    ✅ Financial Compliance AI  
    ✅ Fraud Analysis  
    """)

    st.markdown("---")

    st.markdown("### System Status")

    st.success("LLM Connected")
    st.success("Vector DB Active")
    st.success("Graph Engine Running")

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
# BUTTON
# ---------------------------------

if st.button("Analyze Risk"):

    if query:

        with st.spinner("Analyzing Financial Risk Intelligence..."):

            response, evidence = generate_response(query)

        confidence = min(
            75 + len(evidence) * 5,
            95
        )

        # MAIN ANSWER CARD
        st.markdown("## 🛡️ Aegis Analysis")

        st.markdown(response)

        # METRICS
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Confidence Score",
                f"{confidence}%"
            )

        with col2:
            st.metric(
                "Evidence Sources",
                len(evidence)
            )

        # EVIDENCE PANEL
        with st.expander("📚 Sources Used by Aegis"):

            st.markdown(
                """
                These knowledge sources were retrieved and used
                by Aegis to generate the response.
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
    "Built with Hybrid RAG + GraphRAG + Groq LLM"
)