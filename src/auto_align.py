"""Tự động tìm kiếm chunk chứa nội dung trả lời đúng cho từng câu hỏi và gán exact evidence."""
import json
import re

chunks = json.load(open("data/chunks.json", encoding="utf-8"))
questions = json.load(open("data/benchmark_questions.json", encoding="utf-8"))

# Định nghĩa từ khóa đặc trưng nhận diện đoạn văn cho từng câu
QUESTION_PATTERNS = {
    "q01": ("15 tiết", "Một tín chỉ được quy định bằng 15 tiết học lý thuyết"),
    "q02": ("thang điểm 10", "Điểm học phần được tính theo thang điểm 10"),
    "q03": ("hai lần liên tiếp", "Số lần cảnh báo học tập vượt quá hai lần liên tiếp"),
    "q04": ("sai khác giữa phiếu ghi điểm", "Khi phát hiện có sự sai khác giữa phiếu ghi điểm và điểm trên trang website"),
    "q05": ("điểm D trở lên", "Học phần được tính là tích lũy nếu có điểm học phần đạt từ điểm D trở lên"),
    "q06": ("1,5 lần", "không vượt quá 1,5 lần đối với khoá học từ 4 đến dưới 5 năm"),
    "q07": ("nghỉ học tạm thời", "xin nghỉ học tạm thời và bảo lưu kết quả đã học"),
    "q08": ("hoãn thi", "làm đơn xin hoãn thi nộp cho Ban Quản lý đào tạo"),
    "q09": ("buổi học đầu tiên", "chỉ định vào buổi học đầu tiên của học phần"),
    "q10": ("Sinh viên Xuất sắc", "Sinh viên Xuất sắc: Điểm TBCHT từ 3,60 trở lên và ĐRL đạt từ 90 điểm trở lên"),
    "q11": ("thang điểm 100", "được đánh giá theo thang điểm 100"),
    "q12": ("Loại Tốt", "Từ 80 đến 89 điểm: Loại Tốt"),
    "q13": ("loại Trung bình", "Điểm rèn luyện không vượt quá loại Trung bình"),
    "q14": ("Trạm Y tế", "Trạm Y tế Học viện: Nằm cạnh Giảng đường A"),
    "q15": ("Văn phòng KTX", "Ban Quản lý Ký túc xá sinh viên - Văn phòng KTX"),
    "q21": ("15 tuần học", "mỗi kỳ học chính có 15 tuần học và 04 tuần thi"),
    "q22": ("15 ngày", "hoàn thành trong thời hạn 15 ngày kể từ ngày nhập học"),
    "q23": ("9 - 10 tín chỉ", "phải đăng ký học thêm 9 - 10 tín chỉ tự chọn trong phần chuyên môn"),
    "q24": ("ngày 30 các tháng", "vào ngày 30 các tháng: 3, 5, 7, 9, 11 và 12 hàng năm"),
    "q25": ("xét tốt nghiệp sớm hơn", "đủ điều kiện tốt nghiệp sớm hơn so với thời gian thiết kế của khoá học"),
    "q16": ("14 tín chỉ", "Số tín chỉ tối thiểu trong một học kỳ chính: 14 tín chỉ"),
    "q17": ("trừ 25 điểm", "Thi hộ hoặc nhờ người thi hộ: trừ 25 điểm"),
    "q18": ("bậc 3", "chuẩn năng lực bậc 3 theo Khung năng lực ngoại ngữ 6 bậc"),
    "q19": ("khiển trách", "kỷ luật từ mức khiển trách trở lên trong học kỳ xét học bổng"),
    "q20": ("năm thứ hai", "khi đã được xếp trình độ năm thứ hai của chương trình thứ nhất"),
    "q31": ("Trạm y tế", "Giấy xác n hận ốm phải có dấu tròn của Trạm y tế"),
    "q32": ("gia đình sinh viên", "02 bản gửi về địa phương nơi cư trú và gia đình sinh viên"),
    "q33": ("kỳ học hè", "Trưởng ban Quản lý đào tạo đề nghị Giám đốc Học viện quyết định thêm kỳ học hè")
}


def find_in_chunks(pattern, fallback):
    for c in chunks:
        if pattern.lower() in c["text"].lower():
            # Tìm đoạn câu chứa pattern
            text = c["text"]
            idx = text.lower().find(pattern.lower())
            start = max(0, text.rfind("\n", 0, idx) + 1)
            end = text.find("\n", idx + len(pattern))
            if end == -1:
                end = len(text)
            snippet = text[start:end].strip()
            # Bỏ ký tự đầu dòng thừa
            snippet = re.sub(r"^[-0-9a-zA-Z\.\)]+\s*", "", snippet)
            if len(snippet) > 15:
                return c["page"], snippet, c["id"]
            return c["page"], pattern, c["id"]
    return None, None, None


matched = 0
for q in questions:
    qid = q["id"]
    if qid in QUESTION_PATTERNS:
        pat, sample = QUESTION_PATTERNS[qid]
        page, snippet, cid = find_in_chunks(pat, sample)
        if page and snippet:
            # Tìm chunk chứa snippet
            q["gold"] = [{
                "source_id": "so_tay_sinh_vien_k67",
                "page": page,
                "evidence": snippet
            }]
            print(f"[MATCHED] {qid}: Page {page} | Chunk {cid} | Snippet: {repr(snippet[:60])}")
            matched += 1
        else:
            print(f"[FAIL] {qid}: Không tìm thấy pattern '{pat}' trong bất kỳ chunk nào!")

print(f"\nTổng số câu match: {matched}/{len(QUESTION_PATTERNS)}")

with open("data/benchmark_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
