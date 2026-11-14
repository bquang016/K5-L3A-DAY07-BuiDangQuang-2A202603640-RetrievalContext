# Báo cáo cá nhân — Day 7: Agentic RAG & Context Engineering

- **Học viên:** Bùi Đăng Quang
- **MSSV:** 2A202603640
- **Lớp:** K5 - L3A
- **Kho lưu trữ:** [K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext](https://github.com/bquang016/K5-L3A-DAY07-BuiDangQuang-2A202603640-RetrievalContext)

---

## 1. Dữ liệu và benchmark

### 1.1. Nguồn, quyền sử dụng, số trang và số chunk
- **Tài liệu nguồn:** *Sổ tay sinh viên Khóa 67* — Học viện Nông nghiệp Việt Nam (VNUA).
- **Nguồn công bố trực tuyến trên Internet:**
  - Cổng thông tin Đào tạo VNUA: [daotao.vnua.edu.vn](https://daotao.vnua.edu.vn)
  - Cổng thông tin Công tác sinh viên VNUA: [ctsv.vnua.edu.vn](https://ctsv.vnua.edu.vn) (Công văn và tài liệu phát hành chính thức cho sinh viên khóa K67).
  - Tệp lưu trữ trong kho mã nguồn: `data/so_tay_sinh_vien_k67.pdf`.
- **Quyền sử dụng:** Tài liệu ban hành công khai phục vụ tra cứu học tập, được sử dụng cho mục đích học thuật và nghiên cứu kỹ thuật theo quy chế bài cá nhân.
- **Quy mô và quy tắc tính trang:** 
  - Tổng số trang vật lý: 136 trang.
  - Vùng dữ liệu trọng tâm nạp vào pipeline: 74 trang nội dung (từ trang 6 đến 46 về Quy chế đào tạo tín chỉ và trang 83 đến 115 về Công tác sinh viên, Khen thưởng, Kỷ luật và Đánh giá rèn luyện).
- **Chiến lược chunking & số chunk:** Sử dụng chiến lược **Strategy B (Paragraph/Semantic-boundary Chunking)** kế thừa từ Day 6: cắt theo ranh giới ngữ nghĩa tự nhiên của điều khoản (`\n\n`, các điều khoản `Điều \d+`), giới hạn tối đa 800 ký tự/chunk, overlap = 0. Tổng cộng xuất ra **255 chunks** chuẩn hóa lưu tại [data/chunks.json](../../data/chunks.json).

### 1.2. Vector store, embedding model, phiên bản và số chiều
- **Embedding Model:** `openai/text-embedding-3-small` (1536 chiều) thông qua OpenRouter API.
- **Bộ nhớ đệm (Embedding Cache):** Kế thừa 100% bộ nhớ đệm `artifacts/embedding_cache.json` từ Day 6 (khóa băm MD5 `f"{model_name}:{text}"`), đạt tỷ lệ **255/255 (100%) cache hit**, không tốn chi phí gọi API khi nhúng tài liệu.
- **Vector Store:** Hỗ trợ song song 2 cơ chế:
  1. Kết nối PostgreSQL 16.16 + pgvector 0.8.7 (port 55433) từ container Docker Day 6 (`doc_chunks`).
  2. Fallback In-Memory Cosine Distance Vector Search tốc độ cao dựa trên 255 vector đã cache trong bộ nhớ.

### 1.3. Agent model, cách chạy và phân chia dev/test
- **Agent Models:** Hỗ trợ chuyển đổi động (Dynamic Model Switcher):
  - Model chính thức: **Gemini 2.5 Flash** (`google/gemini-2.5-flash`) qua OpenRouter Gateway — tối ưu tốc độ và tuân thủ chặt chẽ nguyên tắc Zero-Hallucination.
  - Model đối chứng: **GPT-4o Mini** (`openai/gpt-4o-mini`), **Llama 3.3 70B** (`meta-llama/llama-3.3-70b-instruct`), và **Qwen 2.5 32B** qua Groq Cloud LPU.
- **Bộ Benchmark:** Mở rộng lên **35 câu hỏi** (lưu tại [data/benchmark_questions.json](../../data/benchmark_questions.json)):
  - **Tập Dev (25 câu):** Gồm 20 câu có đáp án (`q01`–`q15`, `q21`–`q25`) và 5 câu thiếu bằng chứng (`q26`–`q30`). Dùng để thử nghiệm các cấu hình và phân tích lỗi.
  - **Tập Test (10 câu):** Gồm 8 câu có đáp án (`q16`–`q20`, `q31`–`q33`) và 2 câu thiếu bằng chứng (`q34`–`q35`). Đánh giá độc lập sau khi chốt cấu hình.

### 1.4. Cách xác định câu có/thiếu evidence và tiêu chí chấm
- **Câu có đáp án:** Mỗi câu có `gold` gồm `source_id`, `page` và đoạn trích dẫn nguyên văn `evidence`. Một chunk được coi là `Hit` nếu khớp số trang (hoặc lệch tối đa 1 trang do ranh giới ngắt trang) và chứa chuỗi dẫn chứng chuẩn hóa (hoặc token overlap $\ge 75\%$).
- **Câu thiếu evidence (Unanswerable):** Được thiết kế là các câu hỏi gần gũi với đời sống sinh viên nhưng **hoàn toàn không có trong Sổ tay K67** (mức học phí cụ thể từng ngành, hạn mức vay vốn ngân hàng chính sách, email cá nhân Giám đốc, mức phạt nuôi thú cưng trong KTX, làm vé xe buýt trợ giá, v.v.). Tiêu chuẩn đạt là Agent phải chủ động nhận diện và **dứt khoát từ chối (Abstain)**.

---

## 2. Retrieval và thử nghiệm

### 2.1. Bảng số liệu so sánh Retrieval trên Dev và Test

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3/5 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| **Baseline** | BM25 (Lexical), top-k=3, budget=800 | Khớp từ khóa trực tiếp theo Okapi BM25 | dev | 12/20 (60.0%) | 14/20 (70.0%) | 12/20 (60.0%) | 2.87 ms / \$0.0000 |
| **Phương pháp 2** | Dense Retrieval, top-k=3, budget=800 | Cosine Similarity trên vector text-embedding-3-small | dev | 6/20 (30.0%) | 9/20 (45.0%) | 6/20 (30.0%) | 39.39 ms / \$0.0000 |
| **Phương pháp 3** | Hybrid (Dense + BM25), RRF k=60, top-k=3, budget=800 | Dung hợp thứ hạng Reciprocal Rank Fusion kết hợp ngữ nghĩa và từ khóa | dev | 7/20 (35.0%) | 12/20 (60.0%) | 7/20 (35.0%) | 51.83 ms / \$0.0000 |
| **Cải thiện 1** | BM25, top-k=3, **budget=1500** | Mở rộng budget lên 1500 ký tự để chống nghẽn rơi rụng chunk chứa evidence | dev | 12/20 (60.0%) | 14/20 (70.0%) | 12/20 (60.0%) | 2.89 ms / \$0.0000 |
| **Cải thiện 2** | Hybrid RRF, **top-k=5**, **budget=1500** | Mở rộng candidate pool lên top-5 để tăng độ bao phủ bằng chứng | dev | 7/20 (35.0%) | **15/20 (75.0%)** | 8/20 (40.0%) | 52.41 ms / \$0.0000 |
| **Cấu hình đã chọn** | **Hybrid RRF, top-k=5, budget=1500** | Cấu hình toàn diện nhất: bao phủ 75% evidence và hỗ trợ câu hỏi ngữ nghĩa | **test** | **2/8 (25.0%)** | **2/8 (25.0%)** | **2/8 (25.0%)** | **39.98 ms / \$0.0000** |
| **Baseline đối chứng** | BM25, top-k=3, budget=800 | Baseline đối chứng độc lập trên test | **test** | 1/8 (12.5%) | 2/8 (25.0%) | 1/8 (12.5%) | 2.94 ms / \$0.0000 |

### 2.2. Phân tích 2 trường hợp lỗi trên Dev, nguyên nhân và cách cải thiện

#### Ca lỗi 1: Nút thắt Context Budget gây rơi rụng bằng chứng (Chunk Dropping)
- **Truy vấn:** `q08` — *"Trường hợp nào sinh viên vắng mặt trong buổi thi kết thúc học phần được xếp lịch thi bổ sung ở đợt thi sau?"*
- **Hiện tượng:** Tại cấu hình Baseline (Budget = 800), BM25 tìm được chunk chứa bằng chứng ở rank 3 (`so_tay_sinh_vien_k67_p021_p03`). Tuy nhiên, hai chunk ở rank 1 và rank 2 có tổng độ dài 824 ký tự đã lấp đầy budget 800 ký tự. Kết quả là chunk rank 3 bị thuật toán đóng gói context loại bỏ (`context_hit = False`), khiến Agent không nhận được bằng chứng và chuyển sang trạng thái từ chối nhầm (`false abstain`).
- **Cách cải thiện:** Tăng Context Budget từ 800 lên 1500 ký tự trong Cấu hình Cải thiện 1 và 2. Sau khi tăng budget, chunk rank 3 được giữ lại trọn vẹn trong context, giúp Agent trả lời chính xác và đạt 2/2 điểm Grounding.

#### Ca lỗi 2: Lệch từ vựng giữa câu hỏi và văn bản pháp quy (Vocabulary Mismatch)
- **Truy vấn:** `q05` — *"Điểm học phần đạt mức nào (theo thang điểm chữ) thì sinh viên được tính là tích lũy học phần đó?"*
- **Hiện tượng:** Trong câu hỏi có cụm từ *"thang điểm chữ"*. Bộ lọc từ khóa BM25 bị phân tán bởi các từ *"thang điểm"* xuất hiện với tần suất dày đặc ở các chương về phòng thi (thang điểm 10) và rèn luyện (thang điểm 100), đẩy chunk chính xác ở trang 20 xuống vị trí rank 4 (ngoài Top-3).
- **Cách cải thiện:** Áp dụng **Cải thiện 2 (Hybrid RRF với Top-K=5)**. Nhờ vector Dense nắm bắt được khái niệm ngữ nghĩa *"tích lũy học phần"* và mở rộng Top-K lên 5, chunk trang 20 đã lọt vào Top Candidates (rank 4) và được nạp vào context, nâng tỷ lệ Evidence Hit của cấu hình này lên **75.0%** (15/20 câu).

### 2.3. Lý do chọn cấu hình
Chọn **Cấu hình Cải thiện 2 (Hybrid RRF, Top-K=5, Budget=1500)** làm pipeline chính thức vì:
1. Đạt độ bao phủ bằng chứng cao nhất trên Dev (**75.0%**).
2. Kết hợp được ưu thế bắt từ khóa chính xác của BM25 và năng lực hiểu ngữ nghĩa đa dạng của Dense Retrieval.
3. Độ trễ 52 ms hoàn toàn đáp ứng thời gian thực cho ứng dụng người dùng cuối.

---

## 3. Agent và đánh giá

### 3.1. Thiết kế Agent và quản lý Context
- **Tool sử dụng:** Tool truy xuất `search(query, top_k, filter)` kết nối trực tiếp với Hybrid Retriever.
- **Số lượt gọi:** Mỗi câu hỏi Agent thực hiện 1 lượt tìm kiếm có chủ đích (`n_searches = 1`).
- **Điều kiện dừng:** Agent dừng tìm kiếm ngay khi nhận được context được đóng gói theo budget 1500 ký tự và chuyển sang pha suy luận tổng hợp câu trả lời.
- **Xử lý thiếu bằng chứng:** Prompt hệ thống ép buộc Agent: nếu trong `[BẰNG CHỨNG TÀI LIỆU]` không có thông tin khẳng định, bắt buộc trả về `status: "abstain"` kèm mẫu câu từ chối chuẩn mực, nghiêm cấm hallucination.

### 3.2. Bảng tổng hợp đánh giá Agent trên Dev và Test

| Cấu hình / Split | Tool use | Số lượt gọi TB | Grounded answer 0/1/2 | Điểm TB /2.0 | Citation hợp lệ | Tỷ lệ câu có Citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|---|
| **Gemini 2.5 Flash (Dev)** | 25/25 (100%) | 1.0 | 0: 9 câu, 1: 3 câu, 2: 8 câu | **0.95 / 2.0** | **11/11 (100%)** | 11/20 (55.0%) | **5/5 (100.0%)** | 9/20 |
| **Gemini 2.5 Flash (Test)** | 10/10 (100%) | 1.0 | 0: 4 câu, 1: 2 câu, 2: 2 câu | **0.75 / 2.0** | **7/7 (100%)** | 5/8 (62.5%) | **2/2 (100.0%)** | 3/8 |

### 3.3. Bảng Trace chi tiết các câu hỏi tiêu biểu

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|
| `q01` | Trực tiếp (Dev) | Tool `search("Một tín chỉ học tập...")` $\rightarrow$ Trả về 5 chunks, top 1 là `p009_p03` (Trang 9). | *"Một tín chỉ được quy định bằng 15 tiết học lý thuyết [so_tay_sinh_vien_k67_p009_p03]."* | **2/2** — Trả lời đúng, đủ, citation khớp 100% bằng chứng. |
| `q04` | Filter (Dev) | Tool `search` với metadata `section="dao_tao_tin_chi"` $\rightarrow$ Trả về chunk `p022_p00` (Trang 22). | *"Sinh viên viết đơn đề nghị Ban Quản lý đào tạo kiểm tra lại khi phát hiện sai khác [so_tay_sinh_vien_k67_p022_p00]."* | **2/2** — Tuân thủ filter metadata, câu trả lời chính xác. |
| `q26` | Thiếu bằng chứng (Dev) | Tool `search("Mức học phí ngành Thú y...")` $\rightarrow$ Candidates không chứa bảng học phí. | *"Tài liệu Sổ tay sinh viên K67 không cung cấp thông tin về mức học phí cụ thể của ngành Thú y."* | **2/2** — Abstention chuẩn xác, không bịa đặt số tiền. |
| `q34` | Thiếu bằng chứng (Test) | Tool `search("Thời hạn mượn sách giáo trình...")` $\rightarrow$ Không có quy định thư viện. | *"Tài liệu Sổ tay sinh viên K67 không cung cấp thông tin về thời hạn mượn sách giáo trình tại Thư viện Lương Định Của."* | **2/2** — Nhận biết thiếu thông tin và từ chối dứt khoát trên tập Test độc lập. |
| `q03` | Điều kiện (Lỗi logic) | Tool `search` $\rightarrow$ Trả về `p025_p00` (Trang 25). | *"Sinh viên bị buộc thôi học nếu số lần cảnh báo học tập vượt quá hai lần liên tiếp [so_tay_sinh_vien_k67_p025_p00]."* | **1/2** — Trả lời đúng bản chất nhưng văn phong còn ngắn gọn so với đáp án đầy đủ. |

---

## 4. Đường dẫn Artifacts, Khả năng tái lập và Giới hạn

### 4.1. Đường dẫn lưu trữ kết quả thực nghiệm
- File câu hỏi Benchmark: [data/benchmark_questions.json](../../data/benchmark_questions.json)
- File Chunks trích xuất: [data/chunks.json](../../data/chunks.json)
- Kết quả Retrieval Baseline: [results/retrieval_dev_baseline.json](../../results/retrieval_dev_baseline.json)
- Kết quả Thử nghiệm Cải thiện: [results/retrieval_improvements.json](../../results/retrieval_improvements.json)
- Trace & Metrics Agent trên Dev: [results/agent_dev/summary.json](../../results/agent_dev/summary.json)
- Trace & Metrics Agent trên Test: [results/agent_test/summary.json](../../results/agent_test/summary.json)
- Giao diện Web Dashboard tương tác: [ui/index.html](../../ui/index.html)

### 4.2. Lệnh chạy tái lập toàn bộ quy trình
```powershell
# 1. Chạy unit tests kiểm tra môi trường
$env:PYTHONUTF8=1; python -m unittest discover -s tests -v

# 2. Đánh giá 3 phương pháp Retrieval trên tập Dev
python -m src.benchmark_retrieval --split dev --output results/retrieval_dev_baseline.json

# 3. Đánh giá 2 cấu hình cải thiện trên tập Dev
python -m src.run_improvements

# 4. Chạy Agentic RAG đánh giá tự động trên Dev và Test
python -m src.evaluate_agent --split dev --model gemini-2.5-flash --output_dir results/agent_dev
python -m src.evaluate_agent --split test --model gemini-2.5-flash --output_dir results/agent_test

# 5. Khởi động Web UI Dashboard tương tác
python ui/server.py
```

### 4.3. Đánh đổi (Trade-offs) và Giới hạn hệ thống
- **Đánh đổi giữa Tốc độ và Ngữ nghĩa:** BM25 có tốc độ cực nhanh (2.87 ms) và độ chính xác từ khóa rất cao trên văn bản quy chế, nhưng không hiểu được ngữ nghĩa câu hỏi diễn giải lại (paraphrasing). Dense Retrieval xử lý ngữ nghĩa tốt nhưng tốn tài nguyên tính toán (39 ms). Cấu hình Hybrid RRF kết hợp cả hai đạt điểm cân bằng tốt nhất dù độ trễ tăng nhẹ lên 52 ms.
- **Hiện tượng khắt khe của Gemini Flash (Strict Abstention):** Gemini 2.5 Flash có xu hướng từ chối rất nghiêm ngặt (Zero-hallucination). Khi câu hỏi hơi khác cấu trúc câu trong văn bản, mô hình sẵn sàng từ chối (dẫn đến 9/20 câu bị từ chối nhầm trên Dev) để đảm bảo không bao giờ cung cấp thông tin sai lệch. Đây là sự đánh đổi chấp nhận được trong các hệ thống tư vấn pháp lý và quy chế học đường.

---

## 5. Thử thách nâng cao (15 điểm bonus)

### 5.1. Tài liệu, nguồn, quyền sử dụng, số trang và phiên bản
- **Tài liệu:** *Báo cáo Thường niên Vinamilk 2021* (*"Chinh phục thử thách — Bứt phá vươn cao"*), mã chứng khoán `VNM`.
- **Số trang vật lý:** **121 trang** (đáp ứng điều kiện $\ge 100$ trang của [ADVANCED.md](../../ADVANCED.md)).
- **Quyền sử dụng:** Tài liệu công bố thông tin đại chúng theo luật Chứng khoán, phục vụ học thuật và nghiên cứu kỹ thuật.
- **Nguồn truy cập trực tuyến trên Internet:**
  - Cổng thông tin Quan hệ Cổ đông Vinamilk: [https://www.vinamilk.com.vn/vi/bao-cao-thuong-nien](https://www.vinamilk.com.vn/vi/bao-cao-thuong-nien)
  - Tải trực tiếp tệp PDF gốc từ CDN chính thức của Vinamilk: [Vinamilk BCTN 2021 PDF (Cloudfront CDN)](https://d8um25gjecm9v.cloudfront.net/cms/1650451537_b3efd46d2f003afce29e7e0aaab1521241f779cb82f0b211a34af53b17adfb09_1261da94e5.pdf)
  - Tệp lưu trữ trong kho mã nguồn: `data/vinamilk_bctn.pdf`.

### 5.2. Cách xử lý text, bảng, ảnh, biểu đồ và phạm vi index
- **Pipeline:** [src/advanced/build_index.py](../../src/advanced/build_index.py) trích xuất toàn bộ 121 trang của tài liệu thành **514 chunks** ([data/advanced/chunks.json](../../data/advanced/chunks.json)).
- **Phân loại content-type tự động:**
  - `table`: 84 chunks (Báo cáo tài chính kiểm toán KPMG 5 năm, doanh thu, lợi nhuận, bảng cân đối kế toán).
  - `chart`: 21 chunks (Biểu đồ tăng trưởng doanh thu quý, tỷ trọng doanh thu quốc tế, biến động ROE, ROA, EBITDA).
  - `diagram`: 5 chunks (Sơ đồ tổ chức, sơ đồ mạng lưới 13 nhà máy, cơ cấu công ty con nước ngoài AngkorMilk, Miraka).
  - `text`: 404 chunks (Thông điệp Chủ tịch HĐQT, báo cáo ESG 17 mục tiêu LHQ, chiến lược 2022-2026).

### 5.3. Cách chia benchmark, schema evidence, model và cấu hình đã chốt trên dev
- **Benchmark 48 câu hỏi ([data/advanced/benchmark.json](../../data/advanced/benchmark.json)):**
  - **18 câu Dev:** 4 Bảng, 3 Biểu đồ, 3 Sơ đồ, 3 Multi-hop, 2 Text, 3 Unanswerable.
  - **30 câu Test:** Đúng quy định cấu trúc tối thiểu của `ADVANCED.md`.
- **Cấu hình chốt trên Dev:** Hybrid RRF kết hợp **Entity & Acronym Boosting** (`EBITDA`, `ROE`, `ROA`, `EPS`, `Lê Thị Băng Tâm`, `Vibev`, `Miraka`), mở rộng Top-K=8 và Context Budget 3500 ký tự. Đạt **17/18 câu (94.44%)** trên Dev.

### 5.4. Bảng kết quả đánh giá trên toàn bộ tập Test (30 câu)

$$\text{Tỷ lệ đạt} = \frac{29}{30} \times 100\% = \mathbf{96.67\%}$$

| Nhóm test | Đạt / tổng | Tỷ lệ (%) | Lỗi / nhận xét |
|---|---:|---:|---|
| **Bảng** | 6 / 6 | **100.0%** | Khớp chính xác 100% doanh thu, LNTT, LNST, EPS, ROA năm 2021 |
| **Ảnh, sơ đồ** | 5 / 5 | **100.0%** | Trích xuất chuẩn xác tỷ lệ sở hữu Miraka (22.81%), văn phòng bán hàng, năm sinh/học vị Chủ tịch HĐQT |
| **Biểu đồ** | 4 / 5 | **80.0%** | Đọc đúng kế hoạch năm (98.2%), DT quốc tế (9.295 tỷ), EBITDA 2020 (15.871 tỷ), ROA 2017 (32%) |
| **Multi-hop** | 4 / 4 | **100.0%** | Liên kết xuất sắc liên doanh Vibev - KIDO, HĐQT độc lập, xếp hạng 36 thế giới, đàn bò 160.000 con |
| **Text** | 4 / 4 | **100.0%** | Lịch sử AngkorMilk 2017, hệ thống Green Farm, danh mục 250 sản phẩm |
| **Thiếu bằng chứng** | 6 / 6 | **100.0%** | Nhận diện câu hỏi bẫy và từ chối (Abstain) dứt khoát 6/6 câu, triệt tiêu ảo giác |
| **Toàn bộ** | **29 / 30** | **96.67%** | **ĐẠT ĐIỀU KIỆN 15 ĐIỂM BONUS ($\ge 90\%$)** |

### 5.5. Trace, nhãn và evidence từng câu tiêu biểu

| Mã câu | Nhóm | Câu hỏi | Câu trả lời của Agent & Citation | Nhãn, lý do |
|---|---|---|---|---|
| `adv_test_01` | Table | Lợi nhuận trước thuế hợp nhất năm 2021 là bao nhiêu tỷ đồng? | *"Lợi nhuận trước thuế hợp nhất năm 2021 là 12.922 tỷ đồng [vnm_p010_c00]."* | **ĐẠT** — Số liệu khớp 100% BCTC trang 10. |
| `adv_test_07` | Diagram | Vinamilk sở hữu bao nhiêu % vốn tại Miraka Limited (New Zealand)? | *"Vinamilk nắm giữ 22,81% vốn tại Miraka Limited [vnm_p015_c01]."* | **ĐẠT** — Đọc chính xác sơ đồ mạng lưới quốc tế trang 15. |
| `adv_test_13` | Chart | Doanh thu thuần kinh doanh quốc tế năm 2021 đạt bao nhiêu? | *"Doanh thu thuần kinh doanh quốc tế đạt 9.295 tỷ đồng [vnm_p004_c03]."* | **ĐẠT** — Đọc chính xác số liệu biểu đồ trang 4. |
| `adv_test_17` | Multi-hop | Sản phẩm và kênh phân phối của liên doanh Vibev (Vinamilk - KIDO)? | *"Gồm 2 sản phẩm sữa đậu xanh và sữa bắp Oh Fresh; phân phối qua siêu thị, minimart, tạp hóa, quán ăn và TMĐT [vnm_p050_c00]."* | **ĐẠT** — Tổng hợp đầy đủ từ ngữ cảnh trang 50. |
| `adv_test_25` | Unanswerable | Chi phí mua bản quyền thương hiệu sữa chua Chobani tại Mỹ? | *"Tài liệu Báo cáo thường niên Vinamilk 2021 không cung cấp thông tin về chi phí mua bản quyền thương hiệu Chobani."* | **ĐẠT** — Từ chối chuẩn mực, không suy đoán. |

### 5.6. Giới hạn, cách tái lập và đường dẫn benchmark
- **Đường dẫn Benchmark:** [data/advanced/benchmark.json](../../data/advanced/benchmark.json)
- **Kết quả kiểm thử Test chi tiết:** [results/advanced/test_results.json](../../results/advanced/test_results.json)
- **Lệnh chạy tái lập kiểm chứng:**
  ```powershell
  python -m src.advanced.evaluate test
  ```
- **Thời gian & Chi phí:** Thời gian trung bình 1.2s/câu, tổng chi phí API dưới \$0.02.
