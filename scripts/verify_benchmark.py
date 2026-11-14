import json

with open('data/advanced/benchmark.json', encoding='utf-8') as f:
    bench = json.load(f)

with open('data/advanced/chunks.json', encoding='utf-8') as f:
    chunks = {c['id']: c for c in json.load(f)}

all_q = bench['dev'] + bench['test']
found_count = 0
missing = []

for q in all_q:
    if q['type'] == 'unanswerable':
        continue
    cid = q['gold_chunk_id']
    if cid in chunks:
        c = chunks[cid]
        # Check if page matches
        if c['page'] == q['gold_page']:
            found_count += 1
        else:
            missing.append((q['id'], 'Page mismatch', cid, c['page'], q['gold_page']))
    else:
        # try find chunk by page
        page_chunks = [c for c in chunks.values() if c['page'] == q['gold_page']]
        missing.append((q['id'], 'Chunk id not found', cid, len(page_chunks)))

print(f"Verified {found_count} factual questions.")
if missing:
    print(f"Missing/mismatch: {len(missing)}")
    for m in missing[:5]:
        print(" ", m)
else:
    print("All factual questions matched their gold chunk and page perfectly!")
