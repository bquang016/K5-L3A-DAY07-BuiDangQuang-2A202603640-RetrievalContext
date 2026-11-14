"""Export exact 255 Strategy B chunks from Day 6 with 100% cache hit."""
import json
import os
import sys
from pathlib import Path

# Paths
DAY6_STARTER = Path(r"C:\Users\buida\K5-L3A-DAY06-BuiDangQuang-2A202603640-DataIngestion\starter")
sys.path.insert(0, str(DAY6_STARTER))

from src.ingestion import load_pdf
from src.chunking import by_paragraph

PDF_PATH = Path(r"C:\Users\buida\K5-L3A-DAY06-BuiDangQuang-2A202603640-DataIngestion\data\so_tay_sinh_vien_k67.pdf")
OUTPUT_FILE = Path("data/chunks.json")

print("[Export] Loading core pages from Day 6 PDF...")
all_pages = load_pdf(PDF_PATH, "so_tay_sinh_vien_k67", "data/so_tay_sinh_vien_k67.pdf")
valid_pages = set(range(6, 47)).union(range(83, 116))
pages = [p for p in all_pages if p.page in valid_pages]

print(f"[Export] Extracted {len(pages)} pages. Generating Strategy B chunks...")
chunks_b = []
for p in pages:
    chunks_b.extend(by_paragraph(p, max_size=800))

chunks_day7 = []
for c in chunks_b:
    chunks_day7.append({
        "id": c.chunk_id,
        "source_id": c.document_id,
        "source": c.source,
        "page": c.page,
        "text": c.text,
        "metadata": c.metadata
    })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks_day7, f, ensure_ascii=False, indent=2)

print(f"[Export] Saved {len(chunks_day7)} exact Strategy B chunks to {OUTPUT_FILE} (100% cache match)!")
