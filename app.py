import streamlit as st

from src.rag import RAGEngine

# -----------------------------
# Page Config
# -----------------------------

st.set_page_config(
    page_title="SUPER CURVE TERMINAL",
    page_icon="📈",
    layout="wide",
)

# -----------------------------
# Title
# -----------------------------

st.title("📈 SUPER CURVE TERMINAL")

st.caption(
    "Semantic Search + FAISS + RAG"
)

# -----------------------------
# RAG Engine
# -----------------------------

@st.cache_resource
def load_rag():
    return RAGEngine()


rag = load_rag()

# -----------------------------
# Search Box
# -----------------------------

question = st.text_input(
    "検索",
    placeholder="例：GEXについて何と言ってた？",
)

# -----------------------------
# Search
# -----------------------------

if question:

    with st.spinner("検索中..."):

        result = rag.answer(question)

    st.divider()

    st.subheader("📄 Context")

    st.text(result["context"])

else:

    st.info("質問を入力してください。")

# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "SUPER CURVE TERMINAL v0.1"
)