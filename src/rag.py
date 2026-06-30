"""
rag.py

SUPER CURVE TERMINAL RAG Engine
"""

from __future__ import annotations

import pandas as pd

from src.search import semantic_search


class RAGEngine:

    def __init__(
        self,
        top_k: int = 10,
    ):

        self.top_k = top_k

    # --------------------------------------------------
    # Semantic Search
    # --------------------------------------------------

    def search(
        self,
        question: str,
    ) -> pd.DataFrame:

        return semantic_search(
            query=question,
            top_k=self.top_k,
        )

    # --------------------------------------------------
    # Context Builder
    # --------------------------------------------------

    def build_context(
        self,
        df: pd.DataFrame,
    ) -> str:

        if df.empty:
            return ""

        contexts = []

        for _, row in df.iterrows():

            contexts.append(
f"""Date: {row['created_at']}
Account: @{row['account']}
Score: {row['score']:.4f}

{row['text']}

URL:
{row['url']}
"""
            )

        return "\n" + "=" * 80 + "\n".join(contexts)

    # --------------------------------------------------
    # Answer
    # --------------------------------------------------

    def answer(
        self,
        question: str,
    ):

        df = self.search(question)

        context = self.build_context(df)

        return {
            "question": question,
            "context": context,
            "results": df,
        }