import urllib.request

urls = [
    ('BCTN_recent', 'https://d8um25gjecm9v.cloudfront.net/cms/20260319_VNM_Bao_cao_thuong_nien_2025_eae619d5f6.pdf'),
    ('BCTN_2021', 'https://d8um25gjecm9v.cloudfront.net/cms/1650451537_b3efd46d2f003afce29e7e0aaab1521241f779cb82f0b211a34af53b17adfb09_1261da94e5.pdf'),
    ('BCTN_2020', 'https://d8um25gjecm9v.cloudfront.net/cms/1617354921_428a45ccc0746e6cdfa3569800fb919bbf8e6d36b54603862caf12ac95d89383_2e6b53ea3c.pdf'),
]

for label, url in urls:
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as resp:
            cl = int(resp.headers.get('content-length', 0))
            print(f"{label}: {cl / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"{label} error: {e}")
