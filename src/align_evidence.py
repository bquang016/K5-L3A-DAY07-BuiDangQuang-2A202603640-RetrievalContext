import json
import re

chunks = json.load(open("data/chunks.json", encoding="utf-8"))
questions = json.load(open("data/benchmark_questions.json", encoding="utf-8"))

print(f"Tổng số chunks: {len(chunks)}")

for q in questions:
    if not q.get("gold"):
        continue
    qid = q["id"]
    gold = q["gold"][0]
    expected = q["expected_answer"]
    
    # Tìm kiếm các chunks tiềm năng chứa expected_answer hoặc từ khóa câu hỏi
    q_words = [w for w in re.findall(r"\w+", q["question"].lower()) if len(w) > 2]
    
    candidates = []
    for c in chunks:
        c_text_lower = c["text"].lower()
        score = sum(1 for w in q_words if w in c_text_lower)
        candidates.append((score, c))
        
    candidates.sort(key=lambda x: -x[0])
    best_chunk = candidates[0][1]
    
    # Kiểm tra xem gold cũ có match không
    old_match = any(c["page"] == gold["page"] and gold["evidence"] in c["text"] for c in chunks)
    print(f"{qid}: Gold cũ match={old_match} | Best match chunk: {best_chunk['id']} (Page {best_chunk['page']})")
