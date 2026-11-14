import json
import hashlib

cache = json.load(open("artifacts/embedding_cache.json", encoding="utf-8"))
questions = json.load(open("data/benchmark_questions.json", encoding="utf-8"))
model_name = "openai/text-embedding-3-small"

cached_q = 0
for q in questions:
    h = hashlib.md5(f"{model_name}:{q['question']}".encode("utf-8")).hexdigest()
    if h in cache:
        cached_q += 1

print(f"Questions cached: {cached_q}/{len(questions)}")
