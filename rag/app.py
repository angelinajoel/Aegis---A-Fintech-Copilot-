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

        with st.spinner("Running Hybrid RAG Pipeline..."):

            response = generate_response(query)

        st.markdown(
            f"""
            <div class="risk-card">
                <h2>AI Risk Analysis</h2>
                <p>{response}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.caption(
    "Built with Hybrid RAG + GraphRAG + Groq LLM"
)