"""3 Retrieval Methods for Day 7: Dense (pgvector/embeddings), BM25 (lexical), and Hybrid (RRF)."""
import math
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any
from .embeddings import EmbeddingService, cosine_similarity

DB_URL = os.getenv("DATABASE_URL", "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab")


def tokenize(text: str) -> list[str]:
    """Tokenize Vietnamese text to words using NFC lowercase regex."""
    if not text:
        return []
    return re.findall(r"\w+", unicodedata.normalize("NFC", text).casefold())


class DenseRetriever:
    """Dense Retrieval using Day 6 pgvector database or in-memory vector embeddings."""
    name = "Dense Retrieval (Embeddings)"
    def __init__(self, chunks: list[dict], embedding_service: EmbeddingService | None = None, use_db: bool = True):
        self.chunks = chunks
        self.chunk_map = {c["id"]: c for c in chunks}
        self.embedding_service = embedding_service or EmbeddingService()
        self.use_db = use_db
        self.db_available = False
        self.chunk_vectors: list[list[float]] = []

        if self.use_db:
            self._check_db_connection()

        if not self.db_available:
            self._prepare_in_memory_vectors()

    def _check_db_connection(self):
        try:
            import psycopg
            with psycopg.connect(DB_URL, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT count(*) FROM doc_chunks;")
                    cnt = cur.fetchone()[0]
                    if cnt > 0:
                        self.db_available = True
                        print(f"[DenseRetriever] Đã kết nối PostgreSQL pgvector ({cnt} records).")
        except Exception as e:
            print(f"[DenseRetriever] PostgreSQL không sẵn sàng ({e}). Dùng In-Memory Dense Search.")
            self.db_available = False

    def _prepare_in_memory_vectors(self):
        print(f"[DenseRetriever] Chuẩn bị vectors cho {len(self.chunks)} chunks...")
        texts = [c["text"] for c in self.chunks]
        self.chunk_vectors = self.embedding_service.get_embeddings_batch(texts)

    def search(self, query: str, top_k: int = 3, filter_meta: dict | None = None) -> list[dict]:
        query_vec = self.embedding_service.get_embedding(query)
        if not query_vec:
            return []

        # 1. Thử tìm kiếm bằng PostgreSQL pgvector nếu khả dụng
        if self.db_available:
            try:
                import psycopg
                from psycopg.rows import dict_row
                with psycopg.connect(DB_URL, row_factory=dict_row, connect_timeout=3) as conn:
                    with conn.cursor() as cur:
                        filter_clause = ""
                        params = [query_vec, top_k]
                        if filter_meta and "section" in filter_meta:
                            filter_clause = "AND section = %s"
                            params = [query_vec, filter_meta["section"], top_k]

                        cur.execute(f"""
                            SELECT chunk_id, document_id, source, page, text, section, metadata,
                                   1 - (embedding <=> %s::vector) AS score
                            FROM doc_chunks
                            WHERE 1=1 {filter_clause}
                            ORDER BY embedding <=> %s::vector ASC
                            LIMIT %s;
                        """, params if len(params) == 3 else [query_vec, query_vec, top_k])
                        rows = cur.fetchall()
                        results = []
                        for r in rows:
                            cid = r["chunk_id"]
                            chunk_data = self.chunk_map.get(cid, {
                                "id": cid,
                                "source_id": r["document_id"],
                                "source": r["source"],
                                "page": r["page"],
                                "text": r["text"],
                                "metadata": r["metadata"]
                            })
                            results.append({**chunk_data, "score": float(r["score"]), "strategy": "dense_pgvector"})
                        return results
            except Exception as e:
                print(f"[DenseRetriever] Lỗi query PostgreSQL ({e}). Fallback sang in-memory...")

        # 2. In-memory cosine search fallback
        scored = []
        for chunk, vec in zip(self.chunks, self.chunk_vectors):
            if filter_meta:
                # Kiểm tra điều kiện filter nếu có
                chunk_meta = chunk.get("metadata", {})
                match = all(chunk_meta.get(k) == v for k, v in filter_meta.items())
                if not match:
                    continue
            score = cosine_similarity(query_vec, vec)
            scored.append({**chunk, "score": score, "strategy": "dense_inmemory"})

        return sorted(scored, key=lambda x: -x["score"])[:top_k]


class Bm25Retriever:
    """Okapi BM25 Lexical Retrieval with Vietnamese tokenization."""
    name = "BM25 Okapi (Lexical)"
    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.corpus_size = len(chunks)
        self.doc_tokens = [tokenize(c["text"]) for c in chunks]
        self.doc_lens = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_len = sum(self.doc_lens) / max(1, self.corpus_size)

        # Tính Document Frequency (DF)
        df_counter = Counter()
        for tokens in self.doc_tokens:
            df_counter.update(set(tokens))

        # Tính IDF Okapi chuẩn
        self.idf = {}
        for term, df in df_counter.items():
            self.idf[term] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 3, filter_meta: dict | None = None) -> list[dict]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        results = []
        for idx, chunk in enumerate(self.chunks):
            if filter_meta:
                meta = chunk.get("metadata", {})
                if not all(meta.get(k) == v for k, v in filter_meta.items()):
                    continue

            d_tokens = self.doc_tokens[idx]
            d_len = self.doc_lens[idx]
            d_freqs = Counter(d_tokens)

            score = 0.0
            for term in q_tokens:
                if term in d_freqs:
                    freq = d_freqs[term]
                    idf = self.idf.get(term, 0.0)
                    numerator = freq * (self.k1 + 1.0)
                    denominator = freq + self.k1 * (1.0 - self.b + self.b * (d_len / self.avg_doc_len))
                    score += idf * (numerator / denominator)

            if score > 0:
                results.append({**chunk, "score": score, "strategy": "bm25"})

        return sorted(results, key=lambda x: -x["score"])[:top_k]


class HybridRetriever:
    """Hybrid Retrieval combining Dense and BM25 using Reciprocal Rank Fusion (RRF)."""
    name = "Hybrid (Dense + BM25 RRF)"
    def __init__(self, dense_retriever: DenseRetriever, bm25_retriever: Bm25Retriever, rrf_k: int = 60):
        self.dense = dense_retriever
        self.bm25 = bm25_retriever
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 3, filter_meta: dict | None = None, candidate_k: int = 20) -> list[dict]:
        dense_results = self.dense.search(query, top_k=candidate_k, filter_meta=filter_meta)
        bm25_results = self.bm25.search(query, top_k=candidate_k, filter_meta=filter_meta)

        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, dict] = {}

        # 1. Điểm rank từ Dense
        for rank, item in enumerate(dense_results, start=1):
            cid = item["id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            chunk_map[cid] = item

        # 2. Điểm rank từ BM25
        for rank, item in enumerate(bm25_results, start=1):
            cid = item["id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            if cid not in chunk_map:
                chunk_map[cid] = item

        sorted_items = sorted(rrf_scores.items(), key=lambda x: -x[1])
        output = []
        for cid, score in sorted_items[:top_k]:
            item = chunk_map[cid]
            output.append({**item, "score": score, "strategy": "hybrid_rrf"})
        return output
