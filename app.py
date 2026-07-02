"""
app.py

SUPER CURVE TERMINAL
Archive-first Semantic Search UI

Run
---
streamlit run app.py
"""

from __future__ import annotations

import html
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import APP_NAME, DB_FILE, DEFAULT_TOP_K, VERSION
from src.database import tweet_count
from src.search import semantic_search


# ==================================================
# Page Config
# ==================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# CSS
# ==================================================

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

.sc-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 0.2rem;
}

.sc-subtitle {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 1.2rem;
}

.sc-card {
    border: 1px solid rgba(120, 120, 120, 0.25);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
    background: rgba(255, 255, 255, 0.03);
}

.sc-meta {
    color: #777;
    font-size: 0.82rem;
    margin-bottom: 0.45rem;
}

.sc-text {
    white-space: pre-wrap;
    font-size: 0.98rem;
    line-height: 1.65;
}

.sc-url {
    margin-top: 0.55rem;
    font-size: 0.82rem;
}

.sc-score {
    font-weight: 700;
}

.sc-badge {
    display: inline-block;
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    background: rgba(120, 120, 120, 0.18);
    font-size: 0.78rem;
    margin-right: 0.3rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# ==================================================
# DB Helpers
# ==================================================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data(ttl=30)
def get_db_stats() -> dict[str, object]:
    if not Path(DB_FILE).exists():
        return {
            "tweet_count": 0,
            "fts_count": 0,
            "latest": None,
            "oldest": None,
        }

    with get_connection() as conn:
        tweet_total = conn.execute(
            "SELECT COUNT(*) FROM tweets"
        ).fetchone()[0]

        fts_total = conn.execute(
            "SELECT COUNT(*) FROM tweets_fts"
        ).fetchone()[0]

        row = conn.execute(
            """
            SELECT
                MIN(created_at) AS oldest,
                MAX(created_at) AS latest
            FROM tweets
            """
        ).fetchone()

    return {
        "tweet_count": tweet_total,
        "fts_count": fts_total,
        "latest": row["latest"],
        "oldest": row["oldest"],
    }


def fts_search(
    query: str,
    top_k: int = 20,
) -> pd.DataFrame:
    """
    SQLite FTS5 keyword search.
    """

    if not query.strip():
        return pd.DataFrame()

    sql = """
    SELECT
        t.tweet_id,
        t.created_at,
        t.account,
        t.month,
        t.text,
        t.url,
        t.likes,
        t.reposts,
        t.replies,
        t.quotes,
        bm25(tweets_fts) AS score
    FROM tweets_fts
    JOIN tweets t
        ON tweets_fts.tweet_id = t.tweet_id
    WHERE tweets_fts MATCH ?
    ORDER BY bm25(tweets_fts)
    LIMIT ?
    """

    try:
        with get_connection() as conn:
            rows = conn.execute(
                sql,
                (query, top_k),
            ).fetchall()
    except sqlite3.OperationalError:
        return pd.DataFrame()

    return pd.DataFrame(
        [dict(row) for row in rows]
    )


def latest_tweets(
    top_k: int = 20,
) -> pd.DataFrame:
    sql = """
    SELECT
        tweet_id,
        created_at,
        account,
        month,
        text,
        url,
        likes,
        reposts,
        replies,
        quotes
    FROM tweets
    ORDER BY created_at DESC
    LIMIT ?
    """

    with get_connection() as conn:
        rows = conn.execute(
            sql,
            (top_k,),
        ).fetchall()

    return pd.DataFrame(
        [dict(row) for row in rows]
    )


# ==================================================
# Render Helpers
# ==================================================

def render_tweet_card(
    row: pd.Series,
    rank: int,
    mode: str,
) -> None:
    score = row.get("score", None)

    if score is None:
        score_text = ""
    else:
        try:
            score_text = f"<span class='sc-badge'>score {float(score):.4f}</span>"
        except Exception:
            score_text = f"<span class='sc-badge'>score {html.escape(str(score))}</span>"

    created_at = html.escape(str(row.get("created_at", "")))
    account = html.escape(str(row.get("account", "")))
    tweet_id = html.escape(str(row.get("tweet_id", "")))
    url = html.escape(str(row.get("url", "")))
    text = html.escape(str(row.get("text", "")))

    st.markdown(
        f"""
<div class="sc-card">
  <div class="sc-meta">
    <span class="sc-badge">#{rank}</span>
    <span class="sc-badge">{html.escape(mode)}</span>
    {score_text}
    <span>{created_at}</span>
    <span> / @{account}</span>
    <span> / {tweet_id}</span>
  </div>
  <div class="sc-text">{text}</div>
  <div class="sc-url">
    <a href="{url}" target="_blank">Open on X</a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_results(
    df: pd.DataFrame,
    mode: str,
) -> None:
    if df.empty:
        st.info("該当する投稿はありません。")
        return

    st.caption(f"{len(df)}件表示")

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        render_tweet_card(
            row=row,
            rank=i,
            mode=mode,
        )


# ==================================================
# Sidebar
# ==================================================

stats = get_db_stats()

with st.sidebar:
    st.markdown("## SUPER CURVE TERMINAL")
    st.caption(f"Version: {VERSION}")

    st.divider()

    st.metric(
        "Tweets",
        f"{stats['tweet_count']:,}",
    )

    st.metric(
        "FTS",
        f"{stats['fts_count']:,}",
    )

    st.caption(f"Oldest: {stats['oldest']}")
    st.caption(f"Latest: {stats['latest']}")

    st.divider()

    search_mode = st.radio(
        "Search Mode",
        options=[
            "Semantic",
            "FTS",
            "Latest",
        ],
        index=0,
    )

    top_k = st.slider(
        "Top K",
        min_value=3,
        max_value=50,
        value=DEFAULT_TOP_K,
        step=1,
    )

    st.divider()

    st.caption("Semantic: Embedding / FAISS")
    st.caption("FTS: SQLite FTS5 keyword search")
    st.caption("Latest: 最新投稿順")


# ==================================================
# Main
# ==================================================

st.markdown(
    f"""
<div class="sc-title">{APP_NAME}</div>
<div class="sc-subtitle">
Archive-first semantic search terminal for X posts.
</div>
""",
    unsafe_allow_html=True,
)


query = st.text_input(
    "Query",
    value="",
    placeholder="例: 為替介入とドル円 / 日経平均オプションとGEX / 原油とホルムズ海峡",
)


col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    run_button = st.button(
        "Search",
        type="primary",
        use_container_width=True,
    )

with col2:
    clear_button = st.button(
        "Clear",
        use_container_width=True,
    )

if clear_button:
    st.rerun()


# ==================================================
# Search Execution
# ==================================================

if search_mode == "Latest":
    st.markdown("### Latest Tweets")
    df = latest_tweets(top_k=top_k)
    render_results(
        df=df,
        mode="Latest",
    )

elif run_button:
    if not query.strip():
        st.warning("検索語を入力してください。")
        st.stop()

    if search_mode == "Semantic":
        st.markdown("### Semantic Search Results")

        with st.spinner("Embedding search running..."):
            df = semantic_search(
                query=query,
                top_k=top_k,
            )

        render_results(
            df=df,
            mode="Semantic",
        )

    elif search_mode == "FTS":
        st.markdown("### FTS Search Results")

        with st.spinner("FTS search running..."):
            df = fts_search(
                query=query,
                top_k=top_k,
            )

        render_results(
            df=df,
            mode="FTS",
        )

else:
    st.info("検索語を入力して Search を押してください。Latestモードでは最新投稿を表示します。")