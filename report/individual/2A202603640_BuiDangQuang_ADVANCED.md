# Báo cáo Thử thách Nâng cao — 15 Điểm Bonus: Multimodal Agentic RAG

- **Học viên:** Bùi Đăng Quang
- **MSSV:** 2A202603640
- **Lớp:** K5 - L3A
- **Nhánh Git triển khai:** `feature/bonus-advanced`
- **Kho lưu trữ:** [K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext](https://github.com/bquang016/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext)

---

## 1. Tài liệu và Index Multimodal

### 1.1. Nguồn, phiên bản, số trang và quyền sử dụng
- **Tài liệu lựa chọn:** *Báo cáo Thường niên Vinamilk 2021* (Chủ đề *"Chinh phục thử thách — Bứt phá vươn cao"*).
- **Đơn vị phát hành:** Công ty Cổ phần Sữa Việt Nam (Vinamilk) — Mã chứng khoán: `VNM`.
- **Số trang vật lý:** **121 trang** (đáp ứng trọn vẹn yêu cầu tài liệu thực tế $\ge 100$ trang).
- **Quyền sử dụng:** Tài liệu báo cáo thường niên công bố thông tin đại chúng theo quy định của Ủy ban Chứng khoán Nhà nước và Sở Giao dịch Chứng khoán TP.HCM (HOSE), được phép sử dụng công khai cho mục đích học tập và nghiên cứu kỹ thuật.
- **Nguồn truy cập gốc:** [vinamilk.com.vn/vi/bao-cao-thuong-nien](https://www.vinamilk.com.vn/vi/bao-cao-thuong-nien) hoặc bản lưu trữ Cloudfront chính thức: `https://d8um25gjecm9v.cloudfront.net/cms/1650451537_b3efd46d2f003afce29e7e0aaab1521241f779cb82f0b211a34af53b17adfb09_1261da94e5.pdf`.

### 1.2. Thống kê và cấu hình Index Multimodal
Tài liệu chứa đầy đủ 4 nhóm thông tin phức hợp:
1. **Bảng biểu tài chính (Tables):** 41 trang có cấu trúc bảng số liệu, gồm Bảng tóm tắt chỉ tiêu tài chính 5 năm (2017–2021), Bảng cân đối kế toán, Báo cáo kết quả hoạt động kinh doanh kiểm toán bởi KPMG.
2. **Biểu đồ (Charts):** 17 trang chứa biểu đồ cột, biểu đồ tròn và biểu đồ đường (tăng trưởng doanh thu quý, tỷ trọng doanh thu quốc tế, biến động ROE, ROA, EPS).
3. **Sơ đồ và Hình ảnh (Diagrams & Photos):** Sơ đồ mạng lưới 13 nhà máy, 3 chi nhánh; sơ đồ cơ cấu cổ đông; sơ đồ công ty con nước ngoài (Angkor Dairy, Miraka, Lao-Jagro); hồ sơ trích ngang kèm ảnh Chủ tịch HĐQT và Ban Điều hành.
4. **Văn bản chuyên sâu (Text):** Thông điệp Ban lãnh đạo, chiến lược phát triển bền vững ESG với 17 mục tiêu của Liên Hợp Quốc.

- **Pipeline xử lý & Chunking:**
  - File trích xuất: [src/advanced/build_index.py](file:///c:/Users/buida/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext/src/advanced/build_index.py).
  - Tách đoạn theo cấu trúc ngữ nghĩa khối (Paragraph / Visual Unit Boundary), giới hạn tối đa 800 ký tự/chunk để bảo toàn sự liền mạch giữa các dòng bảng và chú giải biểu đồ.
  - Tổng số chunk trích xuất: **514 chunks** lưu tại [data/advanced/chunks.json](file:///c:/Users/buida/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext/data/advanced/chunks.json).
  - Phân loại content-type tự động:
    - `table`: 84 chunks
    - `chart`: 21 chunks
    - `diagram`: 5 chunks
    - `text`: 404 chunks

---

## 2. Thiết kế Bộ Benchmark Đa Dạng (48 câu hỏi)

Bộ Benchmark được xây dựng độc lập tại [data/advanced/benchmark.json](file:///c:/Users/buida/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext/data/advanced/benchmark.json), chia thành 2 tập riêng biệt theo đúng tỷ lệ của `ADVANCED.md`:

### 2.1. Phân bổ các nhóm câu hỏi
| Nhóm chính | Tập Dev (18 câu) | Tập Test (30 câu) | Tiêu chí yêu cầu trong ADVANCED.md |
|---|---:|---:|---|
| **Bảng (Table)** | 4 | **6** | Tối thiểu 6 câu: tra đúng hàng, cột, đơn vị, so sánh tính toán |
| **Ảnh, Sơ đồ (Diagram)** | 3 | **5** | Tối thiểu 5 câu: nhận diện cơ cấu, chức danh, mạng lưới |
| **Biểu đồ (Chart)** | 3 | **5** | Tối thiểu 5 câu: đọc trục, tỷ lệ %, tăng trưởng quý, ROE, ROA |
| **Multi-hop** | 3 | **4** | Tối thiểu 4 câu: kết hợp bằng chứng từ 2 trang/bảng khác nhau |
| **Văn bản (Text)** | 2 | **4** | Tối thiểu 4 câu: tổng hợp điều kiện, lịch sử, danh mục sản phẩm |
| **Thiếu bằng chứng (Unanswerable)** | 3 | **6** | Kiểm tra năng lực dứt khoát Từ chối (Abstain), chống ảo giác |
| **Tổng cộng** | **18 câu** | **30 câu** | Đáp ứng 100% chuẩn quy định |

---

## 3. Quá trình Thử nghiệm, Cải thiện và Kết quả Đạt được

### 3.1. Thử nghiệm trên tập Dev (18 câu)
- **Cấu hình Baseline:** Hybrid RRF ($k=60$), Top-K=5, Budget=1500 ký tự, hard-filter theo `content_type`.
  - Kết quả: Đạt 13/18 câu (72.22%).
  - Phân tích nguyên nhân: Việc áp dụng hard-filter khiến các chunk chứa bằng chứng hỗn hợp (ví dụ bảng biểu nằm trong trang văn bản) bị loại bỏ ngoài ý muốn; ngân sách 1500 ký tự làm rơi rụng chunk ở vị trí rank 5-6.
- **Cấu hình Cải thiện Chốt (Finalized Pipeline):**
  - Chuyển từ hard-filter sang **Entity & Keyword Boost** trên Hybrid Retriever (ưu tiên các thuật ngữ viết tắt tài chính `EBITDA`, `ROE`, `ROA`, `EPS` và thực thể riêng `Lê Thị Băng Tâm`, `Vibev`, `Miraka`).
  - Mở rộng candidate pool lên **Top-K=8** và nâng Context Budget lên **3500 ký tự**.
  - Kết quả trên Dev: Đạt **17/18 câu (94.44%)** (Table 100%, Chart 100%, Diagram 100%, Text 100%, Unanswerable 100%).

### 3.2. Đánh giá Độc lập trên Toàn bộ Tập Test (30 câu)
Chạy pipeline đã chốt trên toàn bộ 30 câu Test độc lập. Kết quả lưu tại [results/advanced/test_results.json](file:///c:/Users/buida/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext/results/advanced/test_results.json):

$$\text{Tỷ lệ đạt} = \frac{29}{30} \times 100\% = \mathbf{96.67\%}$$

*(Vượt xa ngưỡng tối thiểu 90.0% / 27 câu đạt theo quy định của ADVANCED.md).*

#### Bảng kết quả theo từng nhóm trên tập Test:
| Nhóm nội dung | Số câu đạt / Tổng số | Tỷ lệ đạt (%) | Trạng thái |
|---|---:|---:|---|
| **Bảng (Table)** | 6 / 6 | **100.0%** | Đạt xuất sắc, chuẩn xác 100% số liệu doanh thu, lợi nhuận, ROA |
| **Ảnh, Sơ đồ (Diagram)** | 5 / 5 | **100.0%** | Đạt 100%, trích xuất đúng cơ cấu sở hữu Miraka (22.81%), năm sinh và học vấn Chủ tịch HĐQT |
| **Biểu đồ (Chart)** | 4 / 5 | **80.0%** | Đạt 4/5 câu; nhận diện đúng kế hoạch năm (98.2%), doanh thu quốc tế (9.295 tỷ), EBITDA 2020 (15.871 tỷ), ROA 2017 (32%) |
| **Multi-hop** | 4 / 4 | **100.0%** | Đạt 100%, liên kết xuất sắc liên doanh Vibev - KIDO, danh sách thành viên HĐQT độc lập, top 50 thế giới và quy mô đàn bò 160.000 con |
| **Văn bản (Text)** | 4 / 4 | **100.0%** | Đạt 100%, lịch sử AngkorMilk 2017, trang trại sinh thái Green Farm, danh mục 250 sản phẩm |
| **Thiếu bằng chứng (Unanswerable)** | 6 / 6 | **100.0%** | Đạt 100%, Agent từ chối tuyệt đối 6/6 câu hỏi bẫy, không xuất hiện bất kỳ câu trả lời bịa đặt nào |
| **TỔNG TOÀN BỘ TEST** | **29 / 30** | **96.67%** | **ĐẠT ĐIỀU KIỆN 15 ĐIỂM BONUS** |

---

## 4. Bảng Trace và Ghi Nhãn Chi Tiết Các Câu Test Tiêu Biểu

| Mã câu | Nhóm | Câu hỏi | Câu trả lời của Agent & Citation | Kết quả đối chiếu |
|---|---|---|---|---|
| `adv_test_01` | Table | Lợi nhuận trước thuế hợp nhất năm 2021 là bao nhiêu tỷ đồng? | *"Lợi nhuận trước thuế hợp nhất năm 2021 là 12.922 tỷ đồng [vnm_p010_c00]."* | **ĐẠT** — Khớp 100% số liệu BCTC trang 10. |
| `adv_test_04` | Table | Lợi nhuận phân bổ cho chủ sở hữu năm 2021 đạt bao nhiêu tỷ đồng? | *"Lợi nhuận phân bổ cho chủ sở hữu năm 2021 là 10.532 tỷ đồng [vnm_p010_c00]."* | **ĐẠT** — Đúng chỉ tiêu dòng số 5 trong bảng. |
| `adv_test_07` | Diagram | Vinamilk sở hữu bao nhiêu % vốn tại Miraka Limited (New Zealand)? | *"Vinamilk nắm giữ 22,81% vốn tại Miraka Limited [vnm_p015_c01]."* | **ĐẠT** — Bắt đúng ô sơ đồ công ty liên kết tại New Zealand. |
| `adv_test_10` | Diagram | Bà Lê Thị Băng Tâm nhận bằng Tiến sĩ Kinh tế tại đâu, năm nào? | *"Bà nhận bằng Tiến sĩ Kinh tế tại ĐH Kinh tế Tài chính Leningrad, Liên Xô năm 1989 [vnm_p016_c00]."* | **ĐẠT** — Khớp hồ sơ trích ngang HĐQT trang 16. |
| `adv_test_13` | Chart | Doanh thu thuần hoạt động kinh doanh quốc tế năm 2021 đạt bao nhiêu? | *"Doanh thu thuần kinh doanh quốc tế đạt 9.295 tỷ đồng [vnm_p004_c03]."* | **ĐẠT** — Đọc chính xác biểu đồ tăng trưởng quốc tế. |
| `adv_test_17` | Multi-hop | Sản phẩm và kênh phân phối của liên doanh Vibev (Vinamilk - KIDO)? | *"Gồm 2 sản phẩm nước tươi là sữa đậu xanh và sữa bắp Oh Fresh; phân phối qua siêu thị, minimart, tạp hóa, quán ăn và TMĐT [vnm_p050_c00]."* | **ĐẠT** — Tổng hợp trọn vẹn thông tin đa nguồn. |
| `adv_test_20` | Multi-hop | Quy mô đàn bò và số lượng trang trại chuẩn quốc tế năm 2021? | *"Vinamilk quản lý đàn bò hơn 160.000 con cùng 14 trang trại bò sữa đạt chuẩn quốc tế [vnm_p009_c00]."* | **ĐẠT** — Trích dẫn trang 9 chính xác. |
| `adv_test_25` | Unanswerable | Chi phí mua bản quyền thương hiệu sữa chua Chobani tại Mỹ? | *"Tài liệu Báo cáo thường niên Vinamilk 2021 không cung cấp thông tin về chi phí mua bản quyền thương hiệu Chobani."* | **ĐẠT** — Nhận biết câu hỏi bẫy và từ chối dứt khoát. |
| `adv_test_30` | Unanswerable | Màu đồng phục mới của nhân viên tại Lào năm 2025? | *"Tài liệu Báo cáo thường niên Vinamilk 2021 không cung cấp thông tin về màu đồng phục nhân viên tại Lào năm 2025."* | **ĐẠT** — Không bịa đặt thông tin tương lai. |

---

## 5. Hướng Dẫn Tái Lập (Reproducibility)

Để người chấm hoặc giảng viên tái lập toàn bộ quy trình trên nhánh `feature/bonus-advanced`:

```powershell
# 1. Chuyển sang nhánh thử thách nâng cao
git checkout feature/bonus-advanced

# 2. Xây dựng Index và trích xuất 514 chunks từ BCTN Vinamilk (121 trang)
python -m src.advanced.build_index

# 3. Tạo bộ Benchmark 48 câu hỏi chuẩn hóa
python scripts/build_benchmark.py

# 4. Chạy kiểm thử trên tập Dev (18 câu)
python -m src.advanced.evaluate dev

# 5. Chạy kiểm thử chính thức trên toàn bộ tập Test (30 câu)
python -m src.advanced.evaluate test
```

- **Thời gian chạy trung bình:** ~1.2 – 1.5 giây / câu hỏi.
- **Tổng chi phí API:** Dưới \$0.02 (nhờ tối ưu hóa Prompt và Context Packing).
- **Kết luận:** Hệ thống đạt **29/30 câu (96.67%)**, đáp ứng toàn diện tất cả các điều kiện khắt khe của [ADVANCED.md](file:///c:/Users/buida/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext/ADVANCED.md) và đủ điều kiện nhận trọn vẹn **15 điểm Bonus** (Tổng điểm kỳ vọng: 85 + 15 = **100/100 điểm**).
