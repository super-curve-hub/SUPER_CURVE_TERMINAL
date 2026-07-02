# SUPER CURVE TERMINAL

SUPER CURVE TERMINAL は、X / Twitter の公式アーカイブZIPを読み込み、過去ポストを検索可能なローカル知識DBに変換するための検索ターミナルです。

## Release

v1.0.0-archive-alpha

## 概要

このバージョンでは、X公式アーカイブZIPを直接読み込み、投稿データをSQLiteに保存します。

さらに、SQLite FTS5によるキーワード検索と、intfloat/multilingual-e5-base による意味検索を組み合わせ、Streamlit UIから過去ポストを検索できます。

## 実装済み

- X / Twitter 公式アーカイブZIPの直接インポート
- data/tweets.js の解析
- data/account.js の解析
- data/manifest.js の確認
- 投稿データのSQLite保存
- SQLite FTS5による全文検索
- multilingual-e5-base によるEmbedding作成
- FAISSによるSemantic Search
- Streamlitによる検索UI
- 一括コンパイル確認スクリプト
- Playwright差分更新エンジンの土台

## 起動

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
