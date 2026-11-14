import pypdf

reader = pypdf.PdfReader('data/vinamilk_bctn.pdf')

sample_pages = [3, 4, 9, 10, 11, 12, 15, 16, 21, 25, 31, 35, 41, 44, 50, 68, 70, 77, 82, 99]

for p in sample_pages:
    text = reader.pages[p-1].extract_text()
    print(f"=== PAGE {p} ===")
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for l in lines[:12]:
        print(" ", l)
    print("...")
