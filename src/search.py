"""
search.py

Embedding-based Semantic Search
"""

from __future__ import annotations

from pathlib import Path
import sqlite3

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


DB_FILE = Path("data") / "super_curve_terminal.db"
EMBEDDINGS_FILE = Path("data") / "embeddings.npy"
ID_MAP_FILE = Path("data") / "id_map.npy"

MODEL_NAME = "intfloat/multilingual-e5-base"


def get_tweets_by_ids(tweet_ids: list[str]) -> pd.DataFrame:
    if not tweet_ids:
        return pd.DataFrame()

    conn = sqlite3.connect(DB_FILE)

    try:
        placeholders = ",".join(["?"] * len(tweet_ids))

        df = pd.read_sql(
            f"""
            SELECT *
            FROM tweets
            WHERE tweet_id IN ({placeholders})
            """,
            conn,
            params=tweet_ids,
        )

        order = {tid: i for i, tid in enumerate(tweet_ids)}

        df["rank_order"] = df["tweet_id"].astype(str).map(order)

        return (
            df.sort_values("rank_order")
            .drop(columns=["rank_order"])
            .reset_index(drop=True)
        )

    finally:
        conn.close()


class SemanticSearcher:
    def __init__(self):
        if not EMBEDDINGS_FILE.exists():
            raise FileNotFoundError(EMBEDDINGS_FILE)

        if not ID_MAP_FILE.exists():
            raise FileNotFoundError(ID_MAP_FILE)

        self.model = SentenceTransformer(MODEL_NAME)

        self.embeddings = np.load(
            EMBEDDINGS_FILE
        ).astype("float32")

        self.id_map = np.load(
            ID_MAP_FILE,
            allow_pickle=True,
        ).astype(str)

        self.index = faiss.IndexFlatIP(
            self.embeddings.shape[1]
        )

        self.index.add(self.embeddings)

    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.0,
    ) -> pd.DataFrame:

        q = f"query: {query}"

        query_embedding = self.model.encode(
            [q],
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        tweet_ids = []
        score_map = {}

        for score, idx in zip(scores[0], indices[0]):

            if idx < 0:
                continue

            if float(score) < threshold:
                continue

            tweet_id = str(self.id_map[idx])

            tweet_ids.append(tweet_id)
            score_map[tweet_id] = float(score)

        df = get_tweets_by_ids(tweet_ids)

        if df.empty:
            return df

        df["score"] = df["tweet_id"].astype(str).map(score_map)

        return (
            df.sort_values("score", ascending=False)
            .reset_index(drop=True)
        )


def semantic_search(
    query: str,
    top_k: int = 10,
    threshold: float = 0.0,
) -> pd.DataFrame:

    searcher = SemanticSearcher()

    return searcher.search(
        query=query,
        top_k=top_k,
        threshold=threshold,
    )


if __name__ == "__main__":

    df = semantic_search(
        "GEXについて",
        top_k=5,
    )

    print(df[["tweet_id", "created_at", "score", "text"]])