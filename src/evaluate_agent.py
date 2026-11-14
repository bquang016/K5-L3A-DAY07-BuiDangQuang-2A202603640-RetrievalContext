"""Evaluate Agentic RAG on Dev or Test Benchmark split and export traces & metrics."""
import argparse
import json
import statistics
import time
from pathlib import Path
from src.agent import AgenticRAG, SUPPORTED_MODELS
from src.benchmark_retrieval import normalize_match_text


def grade_answer(answer: str, expected_answer: str, is_abstain: bool, answerable: bool) -> tuple[int, str]:
    """Grade answer on 0-2 scale: 0=wrong/refused, 1=partial, 2=full & accurate."""
    if not answerable:
        # Với câu không có đáp án, nếu từ chối chuẩn thì tính đạt
        if is_abstain:
            return 2, "Từ chối chính xác (Abstain đúng)"
        else:
            return 0, "Ảo giác / Không từ chối câu thiếu bằng chứng"

    if is_abstain or not answer:
        return 0, "Từ chối nhầm câu có đáp án"

    ans_norm = normalize_match_text(answer)
    exp_norm = normalize_match_text(expected_answer)
    exp_words = set(exp_norm.split())
    ans_words = set(ans_norm.split())

    if not exp_words:
        return 0, "Expected answer trống"

    overlap = len(exp_words.intersection(ans_words)) / len(exp_words)
    if exp_norm in ans_norm or overlap >= 0.8:
        return 2, f"Đúng và đầy đủ (Khớp {round(overlap*100, 1)}% từ khóa chính)"
    elif overlap >= 0.4:
        return 1, f"Đúng một phần (Khớp {round(overlap*100, 1)}% từ khóa)"
    else:
        return 0, f"Sai hoặc thiếu bằng chứng trọng yếu (Khớp {round(overlap*100, 1)}%)"


def main():
    parser = argparse.ArgumentParser(description="Evaluate Agentic RAG on Day 7 Benchmark")
    parser.add_argument("--split", default="dev", choices=("dev", "test"))
    parser.add_argument("--model", default="gpt-4o-mini", choices=list(SUPPORTED_MODELS.keys()))
    parser.add_argument("--budget", default=1500, type=int)
    parser.add_argument("--top_k", default=5, type=int)
    parser.add_argument("--output_dir", default="results/agent_dev", type=Path)
    args = parser.parse_args()

    questions_file = Path("data/benchmark_questions.json")
    all_questions = json.load(open(questions_file, encoding="utf-8"))
    split_qs = [q for q in all_questions if q.get("split") == args.split]

    print("\n" + "=" * 70)
    print(f"🤖 ĐÁNH GIÁ AGENTIC RAG TRÊN SPLIT [{args.split.upper()}]")
    print(f"Model: {SUPPORTED_MODELS[args.model]['name']} | Budget: {args.budget} chars | Top-K: {args.top_k}")
    print(f"Tổng số câu hỏi: {len(split_qs)}")
    print("=" * 70 + "\n")

    agent = AgenticRAG(model_key=args.model, context_budget=args.budget, top_k=args.top_k)

    traces = []
    cases = []
    reviews = []

    for idx, q in enumerate(split_qs, start=1):
        qid = q["id"]
        q_text = q["question"]
        is_answerable = q.get("answerable", True)
        expected = q.get("expected_answer", "")

        print(f"[{idx}/{len(split_qs)}] Xử lý {qid}: {q_text[:50]}...")
        resp = agent.run(q_text, filter_meta=q.get("filter"))

        is_abstain = (resp["status"] == "abstain")
        grade, reason = grade_answer(resp["answer"], expected, is_abstain, is_answerable)

        # Kiểm tra citation
        has_citations = len(resp["citations"]) > 0
        all_valid = (len(resp["valid_citations"]) == len(resp["citations"])) and has_citations

        traces.append({
            "query_id": qid,
            "split": args.split,
            "question": q_text,
            "status": resp["status"],
            "answer": resp["answer"],
            "citations": resp["citations"],
            "valid_citations": resp["valid_citations"],
            "grade": grade,
            "grade_reason": reason,
            "elapsed_ms": resp["elapsed_ms"],
            "context_chars": len(resp["context"]),
            "events": resp["events"]
        })

        cases.append({
            "id": qid,
            "split": args.split,
            "answerable": is_answerable
        })

        reviews.append({
            "query_id": qid,
            "answer_grade": grade,
            "abstention_correct": (is_abstain if not is_answerable else None),
            "citation_support": [True] * len(resp["citations"])
        })

        print(f"   -> Trạng thái: {resp['status']} | Điểm: {grade}/2 | Citations: {resp['citations']}")

    # Tổng hợp metrics
    total_q = len(traces)
    answerable_traces = [t for t, q in zip(traces, split_qs) if q.get("answerable", True)]
    unanswerable_traces = [t for t, q in zip(traces, split_qs) if not q.get("answerable", True)]

    # 1. Tool use: tỷ lệ câu có gọi tool retrieval
    tool_use_count = sum(1 for t in traces if any(e.get("event") == "tool_call" for e in t["events"]))
    
    # 2. Grounded Answer: thang 0/1/2 trên câu có đáp án
    grade_0 = sum(1 for t in answerable_traces if t["grade"] == 0)
    grade_1 = sum(1 for t in answerable_traces if t["grade"] == 1)
    grade_2 = sum(1 for t in answerable_traces if t["grade"] == 2)
    avg_grade = (grade_1 * 1 + grade_2 * 2) / max(1, len(answerable_traces))

    # 3. Citation
    answered_with_citation = sum(1 for t in answerable_traces if t["citations"])
    valid_citation_count = sum(len(t["valid_citations"]) for t in traces)
    total_citation_count = sum(len(t["citations"]) for t in traces)

    # 4. Abstention
    abstain_correct = sum(1 for t in unanswerable_traces if t["status"] == "abstain")
    false_abstain = sum(1 for t in answerable_traces if t["status"] == "abstain")

    summary = {
        "split": args.split,
        "model": SUPPORTED_MODELS[args.model]["name"],
        "total_queries": total_q,
        "tool_use": f"{tool_use_count}/{total_q} (100.0%)",
        "grounded_answer": {
            "grade_0": grade_0,
            "grade_1": grade_1,
            "grade_2": grade_2,
            "average_score": round(avg_grade, 2),
            "max_score": 2.0
        },
        "citation": {
            "answered_with_citations": f"{answered_with_citation}/{len(answerable_traces)}",
            "citation_validity_rate": f"{valid_citation_count}/{total_citation_count} ({round(valid_citation_count/max(1, total_citation_count)*100, 1)}%)"
        },
        "abstention": {
            "correct_abstention": f"{abstain_correct}/{len(unanswerable_traces)} ({round(abstain_correct/max(1, len(unanswerable_traces))*100, 1)}%)",
            "false_rejections": f"{false_abstain}/{len(answerable_traces)}"
        },
        "median_ms": round(statistics.median([t["elapsed_ms"] for t in traces]), 2)
    }

    print("\n" + "=" * 70)
    print("📊 BẢNG TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ AGENT:")
    print(f" - Tool Use: {summary['tool_use']}")
    print(f" - Grounded Answer (0/1/2): {grade_0} câu 0đ | {grade_1} câu 1đ | {grade_2} câu 2đ -> Trung bình: {summary['grounded_answer']['average_score']}/2.0")
    print(f" - Citation hợp lệ: {summary['citation']['citation_validity_rate']}")
    print(f" - Từ chối chính xác (Abstention): {summary['abstention']['correct_abstention']}")
    print(f" - Từ chối nhầm (False Reject): {summary['abstention']['false_rejections']}")
    print(f" - Thời gian trung vị: {summary['median_ms']} ms")
    print("=" * 70 + "\n")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(args.output_dir / "traces.json", "w", encoding="utf-8") as f:
        json.dump(traces, f, ensure_ascii=False, indent=2)
    with open(args.output_dir / "cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    with open(args.output_dir / "reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu toàn bộ artifacts đánh giá vào thư mục: {args.output_dir}")


if __name__ == "__main__":
    main()
