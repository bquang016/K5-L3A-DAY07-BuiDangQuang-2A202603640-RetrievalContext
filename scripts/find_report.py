import urllib.request
import re

req = urllib.request.Request('https://www.vinamilk.com.vn/vi/bao-cao-thuong-nien', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    matches = re.findall(r'href=[\'"](https://d8um25gjecm9v\.cloudfront\.net/cms/[^\'"]+\.pdf)[\'"]', html)
    print(f"Total found: {len(matches)}")
    for m in set(matches):
        print(m)
