"""
build_embeddings.py

SQLite tweets
    ↓
SentenceTransformer
    ↓
embeddings.npy
id_map.npy
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer


DB_FILE = Path("data") / "super_curve_terminal.db"
EMBEDDINGS_FILE = Path("data") / "embeddings.npy"
ID_MAP_FILE = Path("data") / "id_map.npy"

MODEL_NAME = "intfloat/multilingual-e5-base"


def load_tweets() -> pd.DataFrame:
    conn = sqlite3.connect(DB_FILE)

    try:
        df = pd.read_sql(
            """
            SELECT
                tweet_id,
                text
            FROM tweets
            WHERE text IS NOT NULL
              AND TRIM(text) != ''
            ORDER BY created_at
            """,
            conn,
        )

        return df

    finally:
        conn.close()


def build_texts(df: pd.DataFrame) -> list[str]:
    return [
        f"passage: {text}"
        for text in df["text"].astype(str).tolist()
    ]


def rebuild_embeddings():
    df = load_tweets()

    if df.empty:
        raise ValueError("tweets テーブルにEmbedding対象データがありません。")

    print("=" * 60)
    print("Build Embeddings")
    print("=" * 60)
    print(f"Tweets : {len(df)}")
    print(f"Model  : {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    texts = build_texts(df)

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    id_map = df["tweet_id"].astype(str).to_numpy()

    np.save(EMBEDDINGS_FILE, embeddings)
    np.save(ID_MAP_FILE, id_map)

    print()
    print("=" * 60)
    print("Embedding Build Complete")
    print("=" * 60)
    print(f"Embeddings : {EMBEDDINGS_FILE}")
    print(f"ID Map     : {ID_MAP_FILE}")
    print(f"Shape      : {embeddings.shape}")

    return embeddings, id_map


if __name__ == "__main__":
    rebuild_embeddings()