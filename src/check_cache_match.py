import json
import hashlib

cache = json.load(open("artifacts/embedding_cache.json", encoding="utf-8"))
model_name = "openai/text-embedding-3-small"
chunks = json.load(open("data/chunks.json", encoding="utf-8"))

matched_single = 0
matched_strip = 0
for c in chunks:
    h1 = hashlib.md5(f"{model_name}:{c['text']}".encode("utf-8")).hexdigest()
    h2 = hashlib.md5(f"{model_name}:{c['text'].strip()}".encode("utf-8")).hexdigest()
    if h1 in cache:
        matched_single += 1
    if h2 in cache:
        matched_strip += 1

print(f"Single colon: {matched_single}/{len(chunks)}")
print(f"Single colon strip: {matched_strip}/{len(chunks)}")
