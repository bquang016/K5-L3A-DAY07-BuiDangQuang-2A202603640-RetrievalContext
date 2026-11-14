"""Run experiments for 2 improvement configurations on Dev split."""
import json
from pathlib import Path
from src.embeddings import EmbeddingService
from src.retrievers import DenseRetriever, Bm25Retriever, HybridRetriever
from src.benchmark_retrieval import evaluate_retriever

CHUNKS_FILE = Path("data/chunks.json")
QUESTIONS_FILE = Path("data/benchmark_questions.json")
OUTPUT_FILE = Path("results/retrieval_improvements.json")

print("\n=======================================================")
print(" THỰC NGHIỆM 2 CẤU HÌNH CẢI THIỆN TRÊN SPLIT [DEV]")
print("=======================================================\n")

chunks = json.load(open(CHUNKS_FILE, encoding="utf-8"))
questions = json.load(open(QUESTIONS_FILE, encoding="utf-8"))
dev_questions = [q for q in questions if q.get("split") == "dev"]

embed_service = EmbeddingService()
bm25 = Bm25Retriever(chunks)
dense = DenseRetriever(chunks, embedding_service=embed_service, use_db=False)
hybrid = HybridRetriever(dense, bm25, rrf_k=60)

# Cấu hình Baseline: BM25, Top-K=3, Budget=800
print("[1/3] Đánh giá Baseline: BM25, Top-K=3, Budget=800 chars...")
res_base = evaluate_retriever("Baseline (BM25, Top-K=3, Budget=800)", bm25, dev_questions, budget=800, top_k=3)

# Cải thiện 1: Tăng Context Budget từ 800 lên 1500 chars (chống nghẽn context)
print("[2/3] Cải thiện 1: BM25, Top-K=3, MỞ RỘNG BUDGET=1500 chars...")
res_imp1 = evaluate_retriever("Cải thiện 1 (BM25, Budget=1500 chars)", bm25, dev_questions, budget=1500, top_k=3)

# Cải thiện 2: Hybrid Retrieval (Dense + BM25 RRF), Top-K=5, Budget=1500 chars
print("[3/3] Cải thiện 2: Hybrid RRF, MỞ RỘNG TOP-K=5, BUDGET=1500 chars...")
res_imp2 = evaluate_retriever("Cải thiện 2 (Hybrid RRF, Top-K=5, Budget=1500)", hybrid, dev_questions, budget=1500, top_k=5)

results = [res_base, res_imp1, res_imp2]

print("\n" + "=" * 85)
print(f"{'Cấu hình thử nghiệm':<42} | {'Hit@1':<12} | {'Evidence Hit@3/5':<16} | {'Context Evidence Rate':<10}")
print("-" * 85)
for r in results:
    print(f"{r['strategy']:<42} | {r['hit1']:<12} | {r['evidence_hit3']:<16} | {r['context_evidence_rate']:<10}")
print("=" * 85 + "\n")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({
        "summary": [{k: v for k, v in r.items() if k != "traces"} for r in results],
        "details": results
    }, f, ensure_ascii=False, indent=2)

print(f"Đã lưu kết quả thử nghiệm cải thiện vào: {OUTPUT_FILE}")
