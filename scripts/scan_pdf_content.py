import pypdf
import json
import re

reader = pypdf.PdfReader('data/vinamilk_bctn.pdf')
pages_data = []

for i, page in enumerate(reader.pages):
    page_num = i + 1
    text = page.extract_text() or ""
    text_lower = text.lower()
    
    has_chart = any(k in text_lower for k in ['biểu đồ', 'tốc độ tăng trưởng', 'tỷ trọng']) or ('doanh thu' in text_lower and '%' in text_lower)
    has_table = any(k in text_lower for k in ['bảng', 'báo cáo tài chính', 'bảng cân đối', 'đvt:']) or ('triệu đồng' in text_lower and len(re.findall(r'\d+[\.,]\d+', text)) > 5)
    has_diagram = any(k in text_lower for k in ['sơ đồ tổ chức', 'mô hình hoạt động', 'sơ đồ', 'cơ cấu quản trị'])
    
    pages_data.append({
        'page': page_num,
        'length': len(text),
        'has_chart': has_chart,
        'has_table': has_table,
        'has_diagram': has_diagram,
        'first_line': text.strip().split('\n')[0] if text.strip() else 'EMPTY'
    })

print(f"Total pages: {len(pages_data)}")
chart_pages = [p['page'] for p in pages_data if p['has_chart']]
table_pages = [p['page'] for p in pages_data if p['has_table']]
diagram_pages = [p['page'] for p in pages_data if p['has_diagram']]

print("Pages with charts (count:", len(chart_pages), "):", chart_pages[:20])
print("Pages with tables (count:", len(table_pages), "):", table_pages[:20])
print("Pages with diagrams (count:", len(diagram_pages), "):", diagram_pages[:20])

with open('data/scanned_pages.json', 'w', encoding='utf-8') as f:
    json.dump(pages_data, f, ensure_ascii=False, indent=2)
print("Saved to data/scanned_pages.json")
