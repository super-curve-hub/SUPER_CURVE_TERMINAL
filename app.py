"""
SUPER CURVE TERMINAL
Streamlit App
"""

import streamlit as st

from src.rag import RAGEngine


# -------------------------------------------------
# Page
# -------------------------------------------------

st.set_page_config(
    page_title="SUPER CURVE TERMINAL",
    page_icon="📈",
    layout="wide",
)

# -------------------------------------------------
# Cache
# -------------------------------------------------

@st.cache_resource
def load_engine():
    return RAGEngine(top_k=10)


engine = load_engine()

# -------------------------------------------------
# Header
# -------------------------------------------------

st.title("📈 SUPER CURVE TERMINAL")
st.caption("Playwright × SQLite × Embedding × RAG")

# -------------------------------------------------
# Input
# -------------------------------------------------

question = st.text_input(
    "質問",
    placeholder="例：GEXについて何と言ってた？"
)

# -------------------------------------------------
# Search
# -------------------------------------------------

if question:

    with st.spinner("Searching..."):
        result = engine.answer(question)

    df = result["results"]

    st.subheader("Semantic Search")

    if df.empty:

        st.warning("検索結果がありません。")

    else:

        show = df[
            [
                "created_at",
                "score",
                "account",
                "text",
                "url",
            ]
        ].copy()

        show.columns = [
            "Date",
            "Score",
            "Account",
            "Tweet",
            "URL",
        ]

        st.dataframe(
            show,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("RAG Context")

    st.text_area(
        label="",
        value=result["context"],
        height=500,
    )

else:

    st.info("質問を入力してください。")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------

st.sidebar.title("SUPER CURVE TERMINAL")

pipeline = """
### Pipeline

X
↓
Playwright
↓
Parser
↓
SQLite
↓
Embeddings
↓
Semantic Search
↓
RAG
"""

st.sidebar.markdown(pipeline)

st.sidebar.success("System Ready")