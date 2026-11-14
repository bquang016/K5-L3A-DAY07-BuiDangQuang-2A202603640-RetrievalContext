import json
import re

with open('data/advanced/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

def search_chunks(keywords, ctype=None, limit=3):
    results = []
    for c in chunks:
        if ctype and c['content_type'] != ctype:
            continue
        text_lower = c['text'].lower()
        if all(k.lower() in text_lower for k in keywords):
            results.append(c)
    return results[:limit]

# Kiểm tra các chủ đề
queries = [
    # Bảng
    (['tổng doanh thu', '2021', '61.012'], 'table'),
    (['lợi nhuận sau thuế', '2021', '10.633'], 'table'),
    (['tổng tài sản', '2021', '53.332'], 'table'),
    (['thành viên hđqt', 'lê thị băng tâm'], None),
    (['thù lao', 'hội đồng quản trị'], None),
    (['cơ cấu cổ đông', 'scic'], None),
    
    # Biểu đồ
    (['doanh thu', 'quý 4', 'tăng trưởng'], None),
    (['tỷ trọng', 'doanh thu'], None),
    (['thị phần', 'ngành sữa'], None),
    (['xuất khẩu', 'doanh thu thuần'], None),
    
    # Sơ đồ / Ảnh
    (['sơ đồ tổ chức'], None),
    (['mô hình hoạt động', '13 nhà máy'], None),
    (['hội đồng quản trị', 'ban điều hành'], None),
    (['green farm', 'trang trại sinh thái'], None),
    
    # Multi-hop
    (['vibev', 'kido', '51%'], None),
    (['đàn bò', '160.000', '14 trang trại'], None),
    (['hạng 36', 'top 50'], None),
    
    # Text
    (['sữa học đường', '25 tỉnh'], None),
    (['dielac', '1976'], None),
    (['kpmg', 'kiểm toán'], None)
]

for kw, ct in queries:
    res = search_chunks(kw, ct)
    print(f"Query {kw} (type: {ct}) -> Found {len(res)} chunks")
    for r in res:
        print(f"  [{r['id']}] P{r['page']} ({r['content_type']}): {r['text'][:120]}...")
