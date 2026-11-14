"""Benchmark and compare 3 retrieval methods: Dense, BM25, and Hybrid on Dev/Test split."""
import argparse
import json
import re
import statistics
import time
from pathlib import Path
from src.embeddings import EmbeddingService
from src.retrievers import DenseRetriever, Bm25Retriever, HybridRetriever


def normalize_match_text(text: str) -> str:
    """Lowercase and strip whitespace/punctuation for flexible evidence checking."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def hit(chunk: dict, gold_list: list[dict]) -> bool:
    """Check if chunk matches source_id, page (or adjacent page) and contains evidence."""
    chunk_page = chunk.get("page")
    chunk_text_norm = normalize_match_text(chunk.get("text", ""))
    chunk_words = set(chunk_text_norm.split())

    for g in gold_list:
        gold_page = g.get("page")
        # Chấp nhận trùng trang hoặc lệch tối đa 1 trang do ranh giới ngắt trang PDF
        if abs(chunk_page - gold_page) > 1:
            continue

        evidence_norm = normalize_match_text(g.get("evidence", ""))
        if not evidence_norm:
            continue

        # 1. Trực tiếp xuất hiện chuỗi con đã chuẩn hóa khoảng trắng
        if evidence_norm in chunk_text_norm:
            return True

        # 2. Token overlap cao (>= 75%) để chấp nhận lỗi ngắt dòng / dính chữ nhẹ từ PDF
        evidence_words = set(evidence_norm.split())
        if evidence_words:
            overlap = len(evidence_words.intersection(chunk_words))
            if (overlap / len(evidence_words)) >= 0.75:
                return True

    return False


def pack_context(results: list[dict], budget: int = 800) -> tuple[str, list[str]]:
    """Pack top retrieved chunks into context string within character budget."""
    blocks, ids, seen = [], [], set()
    for c in results:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        block = f"[{c['id']} | {c.get('source', '')} | page {c.get('page', 0)}]\n{c.get('text', '')}"
        candidate = "\n\n".join(blocks + [block])
        if len(candidate) <= budget:
            blocks.append(block)
            ids.append(c["id"])
        elif not blocks:
            # Nếu chunk đầu tiên quá dài, cắt vừa budget
            blocks.append(block[:budget])
            ids.append(c["id"])
            break
    return "\n\n".join(blocks), ids


def evaluate_retriever(name: str, retriever, questions: list[dict], budget: int = 800, top_k: int = 3) -> dict:
    """Evaluate one retriever on answerable questions."""
    # Chỉ tính metrics trên các câu có đáp án (answerable != False và có gold)
    answerable_qs = [q for q in questions if q.get("answerable") is not False and q.get("gold")]
    traces = []
    latencies = []

    for q in answerable_qs:
        start = time.perf_counter()
        results = retriever.search(q["question"], top_k=top_k, filter_meta=q.get("filter"))
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        context, context_ids = pack_context(results, budget=budget)
        marked = [{**c, "hit": hit(c, q["gold"])} for c in results]

        hit1 = bool(marked and marked[0]["hit"])
        hit3 = any(c["hit"] for c in marked)
        context_hit = any(c["hit"] and c["id"] in context_ids for c in marked)

        traces.append({
            "query_id": q["id"],
            "question": q["question"],
            "strategy": name,
            "top_k": top_k,
            "budget": budget,
            "hit1": hit1,
            "hit3": hit3,
            "context_hit": context_hit,
            "elapsed_ms": round(elapsed_ms, 2),
            "results": [{"id": c["id"], "page": c["page"], "score": round(c.get("score", 0), 4), "hit": c["hit"]} for c in marked]
        })

    total = len(answerable_qs)
    sum_hit1 = sum(t["hit1"] for t in traces)
    sum_hit3 = sum(t["hit3"] for t in traces)
    sum_ctx = sum(t["context_hit"] for t in traces)

    return {
        "strategy": name,
        "n_answerable": total,
        "hit1": f"{sum_hit1}/{total} ({round(sum_hit1 / total * 100, 1)}%)" if total else "0/0",
        "evidence_hit3": f"{sum_hit3}/{total} ({round(sum_hit3 / total * 100, 1)}%)" if total else "0/0",
        "context_evidence_rate": f"{sum_ctx}/{total} ({round(sum_ctx / total * 100, 1)}%)" if total else "0/0",
        "hit1_val": round(sum_hit1 / total, 3) if total else 0,
        "hit3_val": round(sum_hit3 / total, 3) if total else 0,
        "ctx_val": round(sum_ctx / total, 3) if total else 0,
        "median_ms": round(statistics.median(latencies), 2) if latencies else 0,
        "traces": traces
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark 3 Retrieval Methods on Day 7 Dataset")
    parser.add_argument("--chunks", default="data/chunks.json", type=Path)
    parser.add_argument("--questions", default="data/benchmark_questions.json", type=Path)
    parser.add_argument("--split", default="dev", choices=("dev", "test"))
    parser.add_argument("--budget", default=800, type=int)
    parser.add_argument("--top_k", default=3, type=int)
    parser.add_argument("--output", default="results/retrieval_benchmark.json", type=Path)
    args = parser.parse_args()

    if not args.chunks.exists():
        raise FileNotFoundError(f"Không tìm thấy file chunks tại {args.chunks}. Hãy chạy src/export_day6.py trước.")
    if not args.questions.exists():
        raise FileNotFoundError(f"Không tìm thấy file câu hỏi tại {args.questions}.")

    with open(args.chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    with open(args.questions, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    split_questions = [q for q in all_questions if q.get("split") == args.split]
    print(f"\n=======================================================")
    print(f" ĐÁNH GIÁ 3 PHƯƠNG PHÁP RETRIEVAL TRÊN SPLIT: [{args.split.upper()}]")
    print(f" Tổng số câu hỏi: {len(split_questions)} (Có đáp án: {len([q for q in split_questions if q.get('answerable') is not False])})")
    print(f" Context Budget: {args.budget} chars | Top-K: {args.top_k}")
    print(f"=======================================================\n")

    embed_service = EmbeddingService()

    # 1. Khởi tạo retrievers
    print("[1/3] Khởi tạo BM25 Lexical Retriever...")
    bm25 = Bm25Retriever(chunks)

    print("[2/3] Khởi tạo Dense Retriever (PostgreSQL pgvector / Embeddings)...")
    dense = DenseRetriever(chunks, embedding_service=embed_service, use_db=True)

    print("[3/3] Khởi tạo Hybrid Retriever (Dense + BM25 RRF)...")
    hybrid = HybridRetriever(dense, bm25, rrf_k=60)

    # 2. Đánh giá
    print("\n--- Đang chạy benchmark BM25 Lexical ---")
    res_bm25 = evaluate_retriever("BM25 (Lexical)", bm25, split_questions, budget=args.budget, top_k=args.top_k)

    print("--- Đang chạy benchmark Dense Retrieval ---")
    res_dense = evaluate_retriever("Dense (pgvector / text-embedding-3-small)", dense, split_questions, budget=args.budget, top_k=args.top_k)

    print("--- Đang chạy benchmark Hybrid Retrieval (RRF) ---")
    res_hybrid = evaluate_retriever("Hybrid (Dense + BM25 RRF)", hybrid, split_questions, budget=args.budget, top_k=args.top_k)

    # 3. Bảng tổng hợp
    results_summary = [res_bm25, res_dense, res_hybrid]

    print("\n" + "=" * 80)
    print(f"{'Phương pháp':<38} | {'Hit@1':<12} | {'Evidence Hit@3':<16} | {'Context Rate':<14} | {'Median ms':<10}")
    print("-" * 80)
    for r in results_summary:
        print(f"{r['strategy']:<38} | {r['hit1']:<12} | {r['evidence_hit3']:<16} | {r['context_evidence_rate']:<14} | {r['median_ms']:<10}")
    print("=" * 80 + "\n")

    # Lưu kết quả
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "split": args.split,
            "budget": args.budget,
            "top_k": args.top_k,
            "summary": [{k: v for k, v in r.items() if k != "traces"} for r in results_summary],
            "details": results_summary
        }, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu kết quả chi tiết vào: {args.output}")


if __name__ == "__main__":
    main()
