import os
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.advanced.agent import AdvancedAgenticRAG

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARK_PATH = ROOT_DIR / "data" / "advanced" / "benchmark.json"
RESULTS_DIR = ROOT_DIR / "results" / "advanced"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\.,\(\)\[\]"\':\n\r\t]', ' ', text)
    return " ".join(text.split())

def evaluate_case(case: dict, agent_output: dict) -> dict:
    q_type = case["type"]
    ans = agent_output["answer"]
    is_abstain = agent_output["is_abstain"]
    candidates = agent_output["candidates"]
    
    passed = False
    reason = ""
    
    if q_type == "unanswerable":
        if is_abstain and ("không cung cấp thông tin" in ans.lower() or "không có thông tin" in ans.lower() or "không chứa thông tin" in ans.lower() or "không đề cập" in ans.lower()):
            passed = True
            reason = "Abstain chuẩn xác khi câu hỏi thiếu bằng chứng trong tài liệu."
        else:
            passed = False
            reason = "Thất bại: Mô hình không từ chối hoặc suy đoán sai lệch."
    else:
        # Factual question
        gold_chunk = case.get("gold_chunk_id", "")
        gold_page = case.get("gold_page", 0)
        
        # Check citation in answer
        has_citation = gold_chunk in ans or f"Trang {gold_page}" in ans or f"p{gold_page:03d}" in ans or f"trang {gold_page}" in ans.lower()
        
        # Extract numbers in gold
        gold_numbers = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', case["gold_answer"])
        ans_clean = ans.replace(",", ".").replace(" ", "")
        
        # Token overlap
        gold_norm = normalize_text(case["gold_answer"])
        ans_norm = normalize_text(ans)
        gold_tokens = set(gold_norm.split())
        ans_tokens = set(ans_norm.split())
        overlap = len(gold_tokens.intersection(ans_tokens)) / len(gold_tokens) if gold_tokens else 0
        
        # Check if at least 70% of gold numbers appear in answer
        num_found = 0
        for num in gold_numbers:
            # clean number for flexible check (e.g. 11.236 or 11236 or 11.235,73)
            num_clean = num.replace(".", "").replace(",", "").replace("%", "")
            if num in ans or num_clean in ans.replace(".", "").replace(",", ""):
                num_found += 1
                
        num_ratio = num_found / len(gold_numbers) if gold_numbers else 1.0
        
        if not is_abstain and (overlap >= 0.35 or (num_ratio >= 0.7 and has_citation)):
            passed = True
            reason = f"Đạt: Trả lời đúng trọng tâm và có căn cứ (Overlap: {overlap:.2f}, Số liệu: {num_found}/{len(gold_numbers)})."
        else:
            passed = False
            if is_abstain:
                reason = "Thất bại: Từ chối nhầm (False Abstain) dù tài liệu có thông tin."
            elif num_ratio < 0.7:
                reason = f"Thất bại: Thiếu số liệu quan trọng ({num_found}/{len(gold_numbers)} khớp)."
            else:
                reason = f"Thất bại: Nội dung chưa sát đáp án chuẩn (Overlap: {overlap:.2f})."
                
    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "type": q_type,
        "gold_answer": case["gold_answer"],
        "gold_page": case.get("gold_page", 0),
        "gold_chunk_id": case.get("gold_chunk_id", ""),
        "agent_answer": ans,
        "is_abstain": is_abstain,
        "passed": passed,
        "reason": reason,
        "latency_tool_ms": agent_output["latency_tool_ms"],
        "latency_total_ms": agent_output["latency_total_ms"]
    }

def run_evaluation(split: str = "dev"):
    print(f"Loading benchmark for split '{split}'...", flush=True)
    with open(BENCHMARK_PATH, encoding='utf-8') as f:
        bench = json.load(f)
        
    questions = bench[split]
    print(f"Total questions to evaluate: {len(questions)}", flush=True)
    
    agent = AdvancedAgenticRAG()
    evaluated = []
    
    passed_count = 0
    cat_stats = {}
    
    for idx, q in enumerate(questions):
        print(f"[{idx+1}/{len(questions)}] Evaluating {q['id']} ({q['category']})...", end=" ", flush=True)
        hint = q['category'] if q['category'] in ['table', 'chart', 'diagram'] else None
        out = agent.answer(q["question"], content_type_hint=hint)
        res = evaluate_case(q, out)
        evaluated.append(res)
        
        cat = q['category']
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "passed": 0}
        cat_stats[cat]["total"] += 1
        
        if res["passed"]:
            passed_count += 1
            cat_stats[cat]["passed"] += 1
            print(f"PASSED ({res['latency_total_ms']}ms)", flush=True)
        else:
            print(f"FAILED: {res['reason']}", flush=True)
            
        time.sleep(0.2)
        
    accuracy = (passed_count / len(questions)) * 100
    print(f"\n=== EVALUATION RESULTS FOR {split.upper()} ===", flush=True)
    print(f"Total passed: {passed_count}/{len(questions)} ({accuracy:.2f}%)", flush=True)
    print("Breakdown by category:", flush=True)
    for cat, stat in cat_stats.items():
        cat_acc = (stat["passed"] / stat["total"]) * 100
        print(f"  - {cat:15s}: {stat['passed']}/{stat['total']} ({cat_acc:.1f}%)", flush=True)
        
    summary = {
        "split": split,
        "total": len(questions),
        "passed": passed_count,
        "accuracy_pct": round(accuracy, 2),
        "categories": cat_stats,
        "cases": evaluated
    }
    
    out_file = RESULTS_DIR / f"{split}_results.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved results to {out_file}", flush=True)
    return summary

if __name__ == "__main__":
    import sys
    split_arg = sys.argv[1] if len(sys.argv) > 1 else "dev"
    run_evaluation(split_arg)
