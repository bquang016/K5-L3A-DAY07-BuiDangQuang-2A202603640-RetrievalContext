import urllib.request
import os
import pypdf

url = 'https://d8um25gjecm9v.cloudfront.net/cms/1650451537_b3efd46d2f003afce29e7e0aaab1521241f779cb82f0b211a34af53b17adfb09_1261da94e5.pdf'
out_path = 'data/vinamilk_bctn.pdf'

print("Downloading Vinamilk Annual Report (7.1 MB)...")
urllib.request.urlretrieve(url, out_path)
print("Done. Checking pages...")

reader = pypdf.PdfReader(out_path)
print("Total pages:", len(reader.pages))
images_count = sum(len(p.images) for p in reader.pages)
print("Total images:", images_count)
print("Sample text from page 5:", reader.pages[4].extract_text()[:300])
