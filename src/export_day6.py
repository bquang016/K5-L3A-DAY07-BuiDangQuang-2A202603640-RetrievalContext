"""Export chunks from Day 6 database or PDF fallback to Day 7 data/chunks.json contract."""
import json
import os
import re
import unicodedata
from pathlib import Path

# Paths
DAY6_DIR = Path(r"C:\Users\buida\K5-L3A-DAY06-BuiDangQuang-2A202603640-DataIngestion")
PDF_PATH = DAY6_DIR / "data" / "so_tay_sinh_vien_k67.pdf"
OUTPUT_PATH = Path("data/chunks.json")
DB_URL = os.getenv("DATABASE_URL", "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00a0", " ").replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def classify_section(page_num: int) -> str:
    if page_num <= 5:
        return "gioi_thieu_chung"
    elif 6 <= page_num <= 46:
        return "dao_tao_tin_chi"
    elif 47 <= page_num <= 82:
        return "phu_luc"
    elif 83 <= page_num <= 100:
        return "cong_tac_sinh_vien"
    elif 101 <= page_num <= 106:
        return "dia_chi_lien_he"
    else:
        return "danh_gia_ren_luyen"


def try_export_from_db():
    try:
        import psycopg
        from psycopg.rows import dict_row

        print(f"[Export] Đang thử kết nối PostgreSQL pgvector: {DB_URL}...")
        with psycopg.connect(DB_URL, row_factory=dict_row, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                # Kiểm tra số lượng chunk theo từng strategy
                cur.execute("SELECT strategy, count(*) FROM doc_chunks GROUP BY strategy ORDER BY count(*) DESC;")
                strategies = cur.fetchall()
                if not strategies:
                    print("[Export] Bảng doc_chunks trống!")
                    return None
                
                chosen_strategy = strategies[0]["strategy"]
                print(f"[Export] Tìm thấy các strategy: {strategies}. Chọn strategy '{chosen_strategy}'.")
                
                cur.execute("""
                    SELECT chunk_id, document_id, source, page, text, section, metadata
                    FROM doc_chunks
                    WHERE strategy = %s
                    ORDER BY page, chunk_id;
                """, (chosen_strategy,))
                rows = cur.fetchall()
                
                chunks = []
                for r in rows:
                    meta = r.get("metadata") or {}
                    if "section" not in meta and r.get("section"):
                        meta["section"] = r["section"]
                    chunks.append({
                        "id": r["chunk_id"],
                        "source_id": r.get("document_id") or "so_tay_sinh_vien_k67",
                        "source": r.get("source") or "so_tay_sinh_vien_k67.pdf",
                        "page": int(r["page"]),
                        "text": r["text"],
                        "metadata": meta
                    })
                print(f"[Export] Đã xuất thành công {len(chunks)} chunks từ database!")
                return chunks
    except Exception as e:
        print(f"[Export] Không thể kết nối Database ({e}). Sẽ dùng cơ chế Fallback trực tiếp từ PDF...")
        return None


def export_from_pdf():
    import pypdf
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file PDF tại: {PDF_PATH}")
    
    print(f"[Export] Đang đọc file PDF: {PDF_PATH}...")
    reader = pypdf.PdfReader(str(PDF_PATH))
    chunks = []
    
    # Phạm vi từ trang 8 đến 105 như trong báo cáo Day 6
    start_page = 8
    end_page = min(105, len(reader.pages))
    
    for page_num in range(start_page, end_page + 1):
        idx = page_num - 1
        page_text = reader.pages[idx].extract_text() or ""
        norm_text = normalize_text(page_text)
        if len(norm_text) < 50:
            continue
        
        section = classify_section(page_num)
        
        # Cắt nhỏ đoạn ~600 ký tự với overlap 100 ký tự (chuẩn Day 6)
        chunk_size = 600
        overlap = 100
        step = chunk_size - overlap
        
        for c_idx, start_pos in enumerate(range(0, len(norm_text), step)):
            chunk_slice = norm_text[start_pos:start_pos + chunk_size]
            if len(chunk_slice) < 50:
                continue
            chunk_id = f"so_tay_sinh_vien_k67_p{page_num:03d}_{c_idx}"
            chunks.append({
                "id": chunk_id,
                "source_id": "so_tay_sinh_vien_k67",
                "source": "so_tay_sinh_vien_k67.pdf",
                "page": page_num,
                "text": chunk_slice,
                "metadata": {
                    "section": section,
                    "page": page_num,
                    "char_count": len(chunk_slice)
                }
            })
            if start_pos + chunk_size >= len(norm_text):
                break
                
    print(f"[Export] Đã tạo thành công {len(chunks)} chunks từ PDF!")
    return chunks


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    chunks = try_export_from_db()
    if not chunks:
        chunks = export_from_pdf()
        
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[Export] Đã lưu {len(chunks)} chunks vào file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
