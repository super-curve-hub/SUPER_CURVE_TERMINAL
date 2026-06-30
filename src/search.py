from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.database import get_tweets_by_ids

DATA_DIR = Path("data")

EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
IDMAP_PATH = DATA_DIR / "id_map.npy"


class SemanticSearcher:
    """
    FAISSによる意味検索クラス
    """

    def __init__(self):

        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-base"
        )

        self.embeddings = np.load(
            EMBEDDINGS_PATH
        ).astype("float32")

        self.id_map = np.load(
            IDMAP_PATH,
            allow_pickle=True
        ).tolist()

        self.index = faiss.IndexFlatIP(
            self.embeddings.shape[1]
        )

        self.index.add(self.embeddings)

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.50,
    ):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        tweet_ids = []

        similarities = []

        for idx, score in zip(indices[0], scores[0]):

            if idx == -1:
                continue

            if score < threshold:
                continue

            tweet_ids.append(
                str(self.id_map[idx])
            )

            similarities.append(
                float(score)
            )

        if len(tweet_ids) == 0:
            return get_tweets_by_ids([])

        df = get_tweets_by_ids(tweet_ids)

        score_map = dict(
            zip(tweet_ids, similarities)
        )

        df["score"] = (
            df["tweet_id"]
            .astype(str)
            .map(score_map)
        )

        return (
            df.sort_values(
                "score",
                ascending=False,
            )
            .reset_index(drop=True)
        )
