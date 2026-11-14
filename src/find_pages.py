import pypdf

reader = pypdf.PdfReader(r"C:\Users\buida\K5-L3A-DAY06-BuiDangQuang-2A202603640-DataIngestion\data\so_tay_sinh_vien_k67.pdf")

queries = [
    ("q01", "15 giờ", "15 tiết"),
    ("q02", "thang điểm 10", "đánh giá bộ phận"),
    ("q03", "buộc thôi học", "02 lần liên tiếp"),
    ("q04", "sai khác giữa phiếu ghi điểm", "Ban Quản lý đào tạo kiểm tra"),
    ("q05", "điểm D trở lên", "tích lũy"),
    ("q06", "hoàn thành khoá học", "1,5 lần"),
    ("q07", "nghỉ học tạm thời", "bảo lưu"),
    ("q08", "hoãn thi", "vắng mặt có lý do"),
    ("q10", "Sinh viên Xuất sắc", "3,60"),
    ("q11", "thang điểm 100", "đánh giá kết quả rèn luyện"),
    ("q12", "Loại Tốt", "Từ 80 đến"),
    ("q13", "kỷ luật từ mức cảnh cáo", "Trung bình"),
    ("q14", "Trạm Y tế", "Giảng đường A"),
    ("q15", "Ký túc xá", "Văn phòng KTX"),
    ("q16", "14 tín chỉ", "tối thiểu"),
    ("q17", "Thi hộ", "trừ 25 điểm"),
    ("q18", "chuẩn năng lực bậc 3", "ngoại ngữ 6 bậc"),
    ("q19", "học bổng", "khiển trách"),
    ("q20", "chương trình thứ hai", "năm thứ hai")
]

for qid, kw1, kw2 in queries:
    found_pages = []
    for idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        if kw1 in txt or kw2 in txt:
            # check printed page number in text
            first_line = txt.strip().split("\n")[0] if txt.strip() else ""
            found_pages.append((idx + 1, first_line[:10]))
    print(f"{qid} ({kw1} / {kw2}) -> Trang vat ly PDF:", found_pages)
