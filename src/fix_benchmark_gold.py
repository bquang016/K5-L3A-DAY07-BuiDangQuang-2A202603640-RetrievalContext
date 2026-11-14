"""Scan data/chunks.json to find exact matching page and text snippet for each benchmark question."""
import json
import re

chunks = json.load(open("data/chunks.json", encoding="utf-8"))
questions = json.load(open("data/benchmark_questions.json", encoding="utf-8"))


def clean(t: str) -> str:
    t = re.sub(r"[^\w\s]", " ", t.lower())
    return " ".join(t.split())


# Danh sách từ khóa mỏ neo và câu trích dẫn chuẩn hóa theo đúng PDF cho từng câu
GROUND_TRUTH_EVIDENCE = {
    "q01": {
        "page": 9,
        "evidence": "Một tín chỉ được quy định bằng 15 tiết học lý thuyết"
    },
    "q02": {
        "page": 18,
        "evidence": "Điểm học phần được tính theo thang điểm 10 và làm tròn đến một số thập phân."
    },
    "q03": {
        "page": 26,
        "evidence": "Đã bị cảnh báo kết quả học tập 02 lần liên tiếp"
    },
    "q04": {
        "page": 22,
        "evidence": "Khi phát hiện có sự sai khác giữa phiếu ghi điểm và điểm trên trang website, sinh viên viết đơn đề nghị Ban Quản lý đào tạo kiểm tra lại"
    },
    "q05": {
        "page": 20,
        "evidence": "Học phần được tính là tích lũy nếu có điểm học phần đạt từ điểm D trở lên"
    },
    "q06": {
        "page": 8,
        "evidence": "không vượt quá 1,5 lần đối với khoá học từ 4 đến dưới 5 năm"
    },
    "q07": {
        "page": 31,
        "evidence": "Sinh viên được quyền viết đơn gửi Giám đốc Học viện xin nghỉ học tạm thời và bảo lưu kết quả đã học"
    },
    "q08": {
        "page": 21,
        "evidence": "Sinh viên vắng mặt có lý do chính đáng ở kỳ thi kết thúc học phần... phải làm đơn xin hoãn thi nộp cho Ban Quản lý đào tạo"
    },
    "q09": {
        "page": 88,
        "evidence": "Mỗi lớp học phần có 01 lớp trưởng do giảng viên giảng dạy học phần chỉ định vào buổi học đầu tiên"
    },
    "q10": {
        "page": 92,
        "evidence": "Sinh viên Xuất sắc: Điểm TBCHT từ 3,60 trở lên và ĐRL đạt từ 90 điểm trở lên"
    },
    "q11": {
        "page": 103,
        "evidence": "Điểm rèn luyện được đánh giá theo thang điểm 100"
    },
    "q12": {
        "page": 104,
        "evidence": "Từ 80 đến 89 điểm: Loại Tốt"
    },
    "q13": {
        "page": 105,
        "evidence": "Nếu bị kỷ luật từ mức cảnh cáo trở lên: Điểm rèn luyện không vượt quá loại Trung bình"
    },
    "q14": {
        "page": 101,
        "evidence": "Trạm Y tế Học viện: Nằm cạnh Giảng đường A"
    },
    "q15": {
        "page": 101,
        "evidence": "Ban Quản lý Ký túc xá sinh viên - Văn phòng KTX"
    },
    "q21": {
        "page": 13,
        "evidence": "Năm học được chia thành hai kỳ học, mỗi kỳ học chính có 15 tuần học và 04 tuần thi."
    },
    "q22": {
        "page": 14,
        "evidence": "Mọi thủ tục đăng ký nhập học phải được hoàn thành trong thời hạn 15 ngày kể từ ngày nhập học"
    },
    "q23": {
        "page": 27,
        "evidence": "phải đăng ký học thêm 9 - 10 tín chỉ tự chọn trong phần chuyên môn"
    },
    "q24": {
        "page": 28,
        "evidence": "Thời gian xét đủ điều kiện tốt nghiệp cho sinh viên các khóa vào ngày 30 các tháng: 3, 5, 7, 9, 11 và 12"
    },
    "q25": {
        "page": 28,
        "evidence": "Có đơn gửi Ban Quản lý đào tạo đề nghị được xét tốt nghiệp trong trường hợp đủ điều kiện tốt nghiệp sớm hơn"
    },
    "q16": {
        "page": 16,
        "evidence": "Số tín chỉ tối thiểu trong một học kỳ chính: 14 tín chỉ"
    },
    "q17": {
        "page": 105,
        "evidence": "Thi hộ hoặc nhờ người thi hộ: trừ 25 điểm"
    },
    "q18": {
        "page": 30,
        "evidence": "chuẩn năng lực bậc 3 theo Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam"
    },
    "q19": {
        "page": 90,
        "evidence": "Không xét học bổng đối với sinh viên bị kỷ luật từ mức khiển trách trở lên"
    },
    "q20": {
        "page": 25,
        "evidence": "được đăng ký học chương trình thứ hai sớm nhất khi đã được xếp trình độ năm thứ hai"
    },
    "q31": {
        "page": 31,
        "evidence": "Giấy xác n hận ốm phải có dấu tròn của Trạm y tế, Bệnh viện."
    },
    "q32": {
        "page": 93,
        "evidence": "02 bản gửi về địa phương nơi cư trú và gia đình sinh viên"
    },
    "q33": {
        "page": 13,
        "evidence": "Trường hợp đặc biệt, Trưởng ban Quản lý đào tạo đề nghị Giám đốc Học viện quyết định thêm kỳ học hè."
    }
}

updated_count = 0
for q in questions:
    qid = q["id"]
    if qid in GROUND_TRUTH_EVIDENCE:
        info = GROUND_TRUTH_EVIDENCE[qid]
        page = info["page"]
        ev = info["evidence"]
        
        # Tìm chunk thực tế tại page chứa ev
        target_chunk = None
        for c in chunks:
            if c["page"] == page and clean(ev) in clean(c["text"]):
                target_chunk = c
                break
        
        if not target_chunk:
            # Thử tìm ở bất kỳ trang nào
            for c in chunks:
                if clean(ev) in clean(c["text"]):
                    target_chunk = c
                    page = c["page"]
                    break
        
        if target_chunk:
            # Trích xuất chuỗi exact substring từ chunk.text
            c_text = target_chunk["text"]
            # Cập nhật gold
            q["gold"] = [{
                "source_id": "so_tay_sinh_vien_k67",
                "page": page,
                "evidence": ev
            }]
            print(f"[OK] {qid} -> Page {page} (Chunk {target_chunk['id']})")
            updated_count += 1
        else:
            print(f"[WARN] Chưa khớp được {qid} với bất kỳ chunk nào: {ev}")

print(f"\nĐã đồng bộ thành công {updated_count} câu hỏi có đáp án với chunks!")
with open("data/benchmark_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
