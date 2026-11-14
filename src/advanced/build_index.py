import os
import json
import re
import pypdf
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PDF_PATH = ROOT_DIR / "data" / "vinamilk_bctn.pdf"
OUTPUT_CHUNKS_PATH = ROOT_DIR / "data" / "advanced" / "chunks.json"
OUTPUT_DIR = ROOT_DIR / "data" / "advanced"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def classify_content_type(text: str, page_num: int) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ['sơ đồ tổ chức', 'mô hình hoạt động', 'sơ đồ cơ cấu', 'cơ cấu quản trị', 'sơ đồ']):
        return 'diagram'
    if any(k in text_lower for k in ['bảng cân đối', 'chỉ tiêu 2017', 'chỉ tiêu 2021', 'báo cáo tài chính hợp nhất', 'thuyết minh báo cáo', 'stt', 'đvt:']) or ('triệu đồng' in text_lower and len(re.findall(r'\d+[\.,]\d+', text)) > 5):
        return 'table'
    if any(k in text_lower for k in ['biểu đồ', 'tốc độ tăng trưởng', 'tỷ trọng']) or ('doanh thu' in text_lower and '%' in text_lower and any(yr in text for yr in ['2020', '2021', '2019'])):
        return 'chart'
    return 'text'

def extract_chunks():
    print(f"Reading PDF from {PDF_PATH}...")
    reader = pypdf.PdfReader(str(PDF_PATH))
    total_pages = len(reader.pages)
    
    chunks = []
    
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        text = re.sub(r'[ \t]+', ' ', raw_text).strip()
        if not text:
            continue
            
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        current_block = []
        current_len = 0
        chunk_idx = 0
        
        for p in paragraphs:
            p_len = len(p)
            if current_len + p_len > 800 and current_block:
                block_text = "\n".join(current_block)
                ctype = classify_content_type(block_text, page_num)
                chunks.append({
                    "id": f"vnm_p{page_num:03d}_c{chunk_idx:02d}",
                    "source": "vinamilk_bctn_2021",
                    "page": page_num,
                    "content_type": ctype,
                    "text": block_text,
                    "char_count": len(block_text)
                })
                chunk_idx += 1
                current_block = [p]
                current_len = p_len
            else:
                current_block.append(p)
                current_len += p_len + 1
                
        if current_block:
            block_text = "\n".join(current_block)
            ctype = classify_content_type(block_text, page_num)
            chunks.append({
                "id": f"vnm_p{page_num:03d}_c{chunk_idx:02d}",
                "source": "vinamilk_bctn_2021",
                "page": page_num,
                "content_type": ctype,
                "text": block_text,
                "char_count": len(block_text)
            })

    print(f"Total extracted sub-chunks: {len(chunks)}")
    counts = {}
    for c in chunks:
        counts[c['content_type']] = counts.get(c['content_type'], 0) + 1
    print("Content type breakdown:", counts)
    
    with open(OUTPUT_CHUNKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved chunks to {OUTPUT_CHUNKS_PATH}")

if __name__ == "__main__":
    extract_chunks()
