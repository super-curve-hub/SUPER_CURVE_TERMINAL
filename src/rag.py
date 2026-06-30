from __future__ import annotations

import pandas as pd

from src.search import SemanticSearcher


class RAGEngine:
    """
    Retrieval-Augmented Generation

    役割
    ----
    1. Semantic Search
    2. Context生成
    """

    def __init__(self):

        self.searcher = SemanticSearcher()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ) -> pd.DataFrame:

        return self.searcher.semantic_search(
            question,
            top_k=top_k,
        )

    def build_context(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        df = self.retrieve(
            question,
            top_k=top_k,
        )

        if df.empty:
            return "関連する投稿は見つかりませんでした。"

        context = []

        for _, row in df.iterrows():

            context.append(
f"""
日時: {row.created_at}
アカウント: {row.account}
スコア: {row.score:.3f}

投稿:
{row.text}
"""
            )

        return "\n------------------------\n".join(context)

    def answer(
        self,
        question: str,
    ):

        context = self.build_context(question)

        return {
            "question": question,
            "context": context,
        }