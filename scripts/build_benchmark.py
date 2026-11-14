import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_PATH = ROOT_DIR / "data" / "advanced" / "benchmark.json"

dev_questions = [
    # Nhóm Bảng (4 câu)
    {
        "id": "adv_dev_01",
        "category": "table",
        "question": "Theo Bảng tóm tắt thông tin tài chính 2017-2021, tổng doanh thu hợp nhất của Vinamilk năm 2021 đạt bao nhiêu tỷ đồng?",
        "gold_answer": "Tổng doanh thu hợp nhất của Vinamilk năm 2021 đạt 61.012 tỷ đồng.",
        "gold_evidence": "CHỈ TIÊU 2017 2018 2019 2020 2021\nTổng doanh thu 51.135 52.629 56.400 59.723 61.012",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_02",
        "category": "table",
        "question": "Lợi nhuận sau thuế hợp nhất của Vinamilk trong năm 2020 và 2021 lần lượt là bao nhiêu tỷ đồng theo bảng số liệu tài chính?",
        "gold_answer": "Lợi nhuận sau thuế hợp nhất năm 2020 là 11.236 tỷ đồng và năm 2021 là 10.633 tỷ đồng.",
        "gold_evidence": "Lợi nhuận sau thuế 10.278 10.206 10.554 11.236 10.633",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_03",
        "category": "table",
        "question": "Theo bảng chỉ tiêu tài chính, chỉ số Lãi cơ bản trên cổ phiếu (EPS) của Vinamilk năm 2021 là bao nhiêu đồng?",
        "gold_answer": "Chỉ số EPS năm 2021 của Vinamilk là 4.517 đồng.",
        "gold_evidence": "Lãi cơ bản trên cổ phiếu\n(đồng) 5.296 5.295 5.478 4.770 4.517",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_04",
        "category": "table",
        "question": "Chỉ số EBITDA hợp nhất của Vinamilk năm 2021 đạt bao nhiêu tỷ đồng theo bảng số liệu?",
        "gold_answer": "EBITDA năm 2021 của Vinamilk đạt 15.132 tỷ đồng.",
        "gold_evidence": "EBITDA 13.558 13.730 14.853 15.871 15.132",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "dev",
        "type": "factual"
    },

    # Nhóm Biểu đồ (3 câu)
    {
        "id": "adv_dev_05",
        "category": "chart",
        "question": "Theo số liệu tăng trưởng, tổng doanh thu hợp nhất năm 2021 của Vinamilk tăng bao nhiêu phần trăm so với năm 2020?",
        "gold_answer": "Tổng doanh thu hợp nhất năm 2021 tăng 2,2% so với năm 2020.",
        "gold_evidence": "Với mức tăng 2,2% so với năm 2020, tổng doanh thu hợp nhất năm 2021 đã đạt 61.012 tỷ đồng",
        "gold_page": 4,
        "gold_chunk_id": "vnm_p004_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_06",
        "category": "chart",
        "question": "Tốc độ tăng trưởng doanh thu hợp nhất của Vinamilk trong Quý 4/2021 đạt xấp xỉ bao nhiêu phần trăm?",
        "gold_answer": "Doanh thu hợp nhất Quý 4/2021 tăng trưởng xấp xỉ 10%.",
        "gold_evidence": "doanh thu hợp nhất quý 4/2021 đã tăng trưởng xấp xỉ 10%, là mức tăng trưởng theo quý nhanh nhất trong gần 5 năm trở lại đây",
        "gold_page": 4,
        "gold_chunk_id": "vnm_p004_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_07",
        "category": "chart",
        "question": "Theo biểu đồ/chỉ số sinh lời tài chính, tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) của Vinamilk năm 2021 đạt bao nhiêu phần trăm?",
        "gold_answer": "ROE của Vinamilk năm 2021 đạt 32%.",
        "gold_evidence": "ROE 43% 39% 37% 36% 32%",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c01",
        "split": "dev",
        "type": "factual"
    },

    # Nhóm Sơ đồ & Ảnh (3 câu)
    {
        "id": "adv_dev_08",
        "category": "diagram",
        "question": "Theo sơ đồ mô hình hoạt động của Vinamilk, công ty con Angkor Dairy Products Co., Ltd tại Campuchia thuộc sở hữu bao nhiêu phần trăm của Vinamilk?",
        "gold_answer": "Angkor Dairy Products Co., Ltd. tại Campuchia thuộc sở hữu 100% của Vinamilk.",
        "gold_evidence": "Angkor dairy\nProducts\nCo.,Ltd. (100%)",
        "gold_page": 15,
        "gold_chunk_id": "vnm_p015_c01",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_09",
        "category": "diagram",
        "question": "Theo sơ đồ mạng lưới hoạt động trong nước, Vinamilk vận hành bao nhiêu nhà máy sản xuất sữa tại các vùng Bắc, Trung, Nam?",
        "gold_answer": "Vinamilk có 13 nhà máy sản xuất sữa tại Bắc, Trung, Nam.",
        "gold_evidence": "13 nhà máy sản xuất sữa tại Bắc, Trung, Nam",
        "gold_page": 15,
        "gold_chunk_id": "vnm_p015_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_10",
        "category": "diagram",
        "question": "Chủ tịch Hội đồng Quản trị Vinamilk bà Lê Thị Băng Tâm đảm nhiệm vị trí Chủ tịch HĐQT từ thời gian nào?",
        "gold_answer": "Bà Lê Thị Băng Tâm đảm nhiệm vị trí Chủ tịch HĐQT Vinamilk từ tháng 7/2015.",
        "gold_evidence": "Bà là thành viên HĐQT của Vinamilk từ tháng 4/2013 và đảm nhiệm vị trí Chủ tịch HĐQT từ tháng 7/2015.",
        "gold_page": 16,
        "gold_chunk_id": "vnm_p016_c00",
        "split": "dev",
        "type": "factual"
    },

    # Nhóm Multi-hop (3 câu)
    {
        "id": "adv_dev_11",
        "category": "multi_hop",
        "question": "Liên doanh Vibev giữa Vinamilk và đối tác nào được thành lập, trong đó Vinamilk nắm giữ bao nhiêu phần trăm cổ phần?",
        "gold_answer": "Liên doanh Vibev được thành lập giữa Vinamilk và CTCP Tập đoàn KIDO, trong đó Vinamilk sở hữu 51%.",
        "gold_evidence": "liên doanh Vibev giữa Vinamilk và CTCP Tập đoàn KIDO, trong đó Vinamilk sở hữu 51%",
        "gold_page": 50,
        "gold_chunk_id": "vnm_p050_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_12",
        "category": "multi_hop",
        "question": "Thương hiệu nước chua/nước tươi nào của liên doanh Vibev đã được ra mắt vào tháng 11/2021 với 2 dòng sản phẩm là sữa đậu xanh và sữa bắp?",
        "gold_answer": "Thương hiệu nước tươi Oh Fresh của liên doanh Vibev.",
        "gold_evidence": "đã chính thức giới thiệu sản phẩm đến người tiêu dùng trong nước với 2 sản phẩm nước tươi là sữa đậu xanh và sữa bắp thương hiệu Oh Fresh",
        "gold_page": 50,
        "gold_chunk_id": "vnm_p050_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_13",
        "category": "multi_hop",
        "question": "Trong cơ cấu HĐQT của Vinamilk, có bao nhiêu thành viên nữ và chiếm tỷ lệ bao nhiêu phần trăm tổng số thành viên?",
        "gold_answer": "HĐQT Vinamilk có 4 thành viên nữ, chiếm 40% tổng số thành viên HĐQT.",
        "gold_evidence": "HĐQT của Vinamilk hiện nay có 04 thành viên là nữ, chiếm 40% tổng số thành viên HĐQT đương nhiệm.",
        "gold_page": 70,
        "gold_chunk_id": "vnm_p070_c00",
        "split": "dev",
        "type": "factual"
    },

    # Nhóm Text (2 câu)
    {
        "id": "adv_dev_14",
        "category": "text",
        "question": "Năm 1976 khi mới thành lập, tiền thân của Vinamilk gồm những nhà máy sữa nào?",
        "gold_answer": "Tiền thân năm 1976 thành lập Nhà máy sữa Thống Nhất, Trường Thọ và sữa bột Dielac.",
        "gold_evidence": "1976\nThành lập Nhà máy sữa Thống Nhất,\nTrường Thọ và sữa bột Dielac.",
        "gold_page": 12,
        "gold_chunk_id": "vnm_p012_c00",
        "split": "dev",
        "type": "factual"
    },
    {
        "id": "adv_dev_15",
        "category": "text",
        "question": "Trong khuôn khổ chương trình Sữa học đường, Vinamilk đã cung cấp sữa tại bao nhiêu tỉnh, thành trên toàn quốc tính đến năm 2021?",
        "gold_answer": "Vinamilk cung cấp Sữa học đường tại 25 tỉnh, thành trên toàn quốc.",
        "gold_evidence": "Cung cấp Sữa học đường tại 25 tỉnh, thành đang thực hiện chương trình Sữa học đường trên toàn quốc.",
        "gold_page": 82,
        "gold_chunk_id": "vnm_p082_c00",
        "split": "dev",
        "type": "factual"
    },

    # Nhóm Thiếu bằng chứng (3 câu)
    {
        "id": "adv_dev_16",
        "category": "unanswerable",
        "question": "Vinamilk dự kiến xây dựng thêm bao nhiêu nhà máy sữa tại Châu Âu trong năm 2025?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không cung cấp thông tin về kế hoạch xây dựng nhà máy sữa tại Châu Âu trong năm 2025.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "dev",
        "type": "unanswerable"
    },
    {
        "id": "adv_dev_17",
        "category": "unanswerable",
        "question": "Giá bán lẻ một hộp sữa chua Vinamilk nha đam tại siêu thị VinMart vào tháng 12/2021 là bao nhiêu tiền?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không có thông tin về giá bán lẻ cụ thể của hộp sữa chua nha đam tại siêu thị VinMart.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "dev",
        "type": "unanswerable"
    },
    {
        "id": "adv_dev_18",
        "category": "unanswerable",
        "question": "Mức lương thưởng chi tiết của nhân viên lái xe bồn chở sữa tại trang trại bò sữa Nghệ An là bao nhiêu triệu đồng mỗi tháng?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không công bố mức lương thưởng cụ thể của nhân viên lái xe bồn tại trang trại Nghệ An.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "dev",
        "type": "unanswerable"
    }
]

test_questions = [
    # Nhóm Bảng (6 câu)
    {
        "id": "adv_test_01",
        "category": "table",
        "question": "Theo Bảng chỉ tiêu tài chính cơ bản 2017-2021, Lợi nhuận trước thuế hợp nhất của Vinamilk năm 2021 là bao nhiêu tỷ đồng?",
        "gold_answer": "Lợi nhuận trước thuế năm 2021 của Vinamilk là 12.922 tỷ đồng.",
        "gold_evidence": "Lợi nhuận trước thuế 12.229 12.052 12.796 13.519 12.922",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_02",
        "category": "table",
        "question": "Tổng doanh thu hợp nhất của Vinamilk trong 3 năm liên tiếp 2019, 2020 và 2021 lần lượt là bao nhiêu tỷ đồng theo bảng số liệu?",
        "gold_answer": "Tổng doanh thu các năm lần lượt là: 2019 đạt 56.400 tỷ đồng, 2020 đạt 59.723 tỷ đồng, và 2021 đạt 61.012 tỷ đồng.",
        "gold_evidence": "Tổng doanh thu 51.135 52.629 56.400 59.723 61.012",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_03",
        "category": "table",
        "question": "Theo bảng chỉ tiêu tài chính, Lãi cơ bản trên một cổ phiếu (EPS) của Vinamilk năm 2020 đạt mức bao nhiêu đồng?",
        "gold_answer": "EPS năm 2020 của Vinamilk đạt 4.770 đồng.",
        "gold_evidence": "Lãi cơ bản trên cổ phiếu\n(đồng) 5.296 5.295 5.478 4.770 4.517",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_04",
        "category": "table",
        "question": "Lợi nhuận phân bổ cho chủ sở hữu của Công ty Vinamilk năm 2021 đạt bao nhiêu tỷ đồng?",
        "gold_answer": "Lợi nhuận phân bổ cho chủ sở hữu năm 2021 là 10.532 tỷ đồng.",
        "gold_evidence": "Lợi nhuận phân bổ cho\nchủ sở hữu của Công ty 10.296 10.227 10.581 11.099 10.532",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_05",
        "category": "table",
        "question": "Tổng doanh thu hợp nhất năm 2017 của Vinamilk được ghi nhận trong bảng tài chính là bao nhiêu tỷ đồng?",
        "gold_answer": "Tổng doanh thu hợp nhất năm 2017 là 51.135 tỷ đồng.",
        "gold_evidence": "Tổng doanh thu 51.135 52.629 56.400 59.723 61.012",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_06",
        "category": "table",
        "question": "Tỷ suất lợi nhuận trên tổng tài sản (ROA) của Vinamilk năm 2021 là bao nhiêu phần trăm theo bảng chỉ số sinh lời?",
        "gold_answer": "ROA của Vinamilk năm 2021 là 21%.",
        "gold_evidence": "ROA 32% 28% 26% 24% 21%",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c01",
        "split": "test",
        "type": "factual"
    },

    # Nhóm Ảnh, sơ đồ (5 câu)
    {
        "id": "adv_test_07",
        "category": "diagram",
        "question": "Theo sơ đồ mạng lưới hoạt động của Vinamilk, công ty Miraka Limited tại New Zealand do Vinamilk nắm giữ bao nhiêu phần trăm vốn?",
        "gold_answer": "Vinamilk nắm giữ 22,81% vốn tại Miraka Limited.",
        "gold_evidence": "Miraka Limited\n(22.81%)",
        "gold_page": 15,
        "gold_chunk_id": "vnm_p015_c01",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_08",
        "category": "diagram",
        "question": "Theo sơ đồ đơn vị trực thuộc, Vinamilk có bao nhiêu chi nhánh văn phòng bán hàng tại Việt Nam?",
        "gold_answer": "Vinamilk có 3 chi nhánh văn phòng bán hàng tại Việt Nam (Hà Nội, Đà Nẵng, Cần Thơ).",
        "gold_evidence": "03 chi nhánh văn phòng bán hàng tại Hà Nội, Đà Nẵng, Cần Thơ",
        "gold_page": 15,
        "gold_chunk_id": "vnm_p015_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_09",
        "category": "diagram",
        "question": "Chủ tịch HĐQT Vinamilk bà Lê Thị Băng Tâm sinh năm bao nhiêu theo hồ sơ trích ngang?",
        "gold_answer": "Bà Lê Thị Băng Tâm sinh năm 1947.",
        "gold_evidence": "Bà Lê Thị Băng Tâm\nChủ tịch HĐQT\nThành viên HĐQT độc lập\nBà sinh năm 1947.",
        "gold_page": 16,
        "gold_chunk_id": "vnm_p016_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_10",
        "category": "diagram",
        "question": "Bà Lê Thị Băng Tâm nhận bằng Tiến sĩ Kinh tế tại trường đại học nào và vào năm nào?",
        "gold_answer": "Bà nhận bằng Tiến sĩ Kinh tế tại Đại học Kinh tế Tài chính Leningrad, Liên Xô năm 1989.",
        "gold_evidence": "Tiến sĩ Kinh tế, Đại học Kinh tế Tài chính Leningrad,\nLiên Xô (năm 1989).",
        "gold_page": 16,
        "gold_chunk_id": "vnm_p016_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_11",
        "category": "diagram",
        "question": "Theo hồ sơ Ban Điều hành, ông Mai Hoài Anh sinh năm bao nhiêu và giữ chức vụ gì tại Vinamilk?",
        "gold_answer": "Ông Mai Hoài Anh sinh năm 1970, giữ chức vụ Giám đốc Điều hành Kinh doanh Quốc tế và Kinh doanh Nội địa.",
        "gold_evidence": "Ông Mai Hoài Anh\nGiám đốc Điều hành Kinh doanh Quốc tế\nvà Kinh doanh Nội địa\nÔng sinh năm 1970.",
        "gold_page": 21,
        "gold_chunk_id": "vnm_p021_c00",
        "split": "test",
        "type": "factual"
    },

    # Nhóm Biểu đồ (5 câu)
    {
        "id": "adv_test_12",
        "category": "chart",
        "question": "Tổng doanh thu hợp nhất năm 2021 của Vinamilk hoàn thành bao nhiêu phần trăm kế hoạch đề ra của năm?",
        "gold_answer": "Hoàn thành 98,2% kế hoạch đề ra của năm.",
        "gold_evidence": "đạt 61.012 tỷ đồng, lần đầu vượt mức 60 nghìn tỷ đồng và hoàn thành 98,2% kế hoạch đề ra",
        "gold_page": 4,
        "gold_chunk_id": "vnm_p004_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_13",
        "category": "chart",
        "question": "Năm 2021, doanh thu thuần từ hoạt động kinh doanh quốc tế của Vinamilk đạt bao nhiêu tỷ đồng?",
        "gold_answer": "Doanh thu thuần hoạt động kinh doanh quốc tế đạt 9.295 tỷ đồng.",
        "gold_evidence": "Doanh thu thuần của hoạt động kinh doanh quốc tế đạt 9.295 tỷ đồng",
        "gold_page": 4,
        "gold_chunk_id": "vnm_p004_c03",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_14",
        "category": "chart",
        "question": "Theo số liệu tài chính, chỉ số EBITDA của Vinamilk năm 2020 đạt mức bao nhiêu tỷ đồng?",
        "gold_answer": "EBITDA năm 2020 đạt 15.871 tỷ đồng.",
        "gold_evidence": "EBITDA 13.558 13.730 14.853 15.871 15.132",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_15",
        "category": "chart",
        "question": "Tỷ suất sinh lời ROE của Vinamilk trong năm 2017 đạt mức bao nhiêu phần trăm theo biểu đồ?",
        "gold_answer": "ROE năm 2017 của Vinamilk đạt 43%.",
        "gold_evidence": "ROE 43% 39% 37% 36% 32%",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c01",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_16",
        "category": "chart",
        "question": "Tỷ suất sinh lời ROA năm 2017 của Vinamilk ghi nhận ở mức bao nhiêu phần trăm?",
        "gold_answer": "ROA năm 2017 của Vinamilk đạt 32%.",
        "gold_evidence": "ROA 32% 28% 26% 24% 21%",
        "gold_page": 10,
        "gold_chunk_id": "vnm_p010_c01",
        "split": "test",
        "type": "factual"
    },

    # Nhóm Multi-hop (4 câu)
    {
        "id": "adv_test_17",
        "category": "multi_hop",
        "question": "Vinamilk và đối tác KIDO ra mắt 2 sản phẩm sữa chua/nước tươi nào dưới thương hiệu Oh Fresh và phân phối qua những kênh nào?",
        "gold_answer": "Ra mắt 2 sản phẩm là sữa đậu xanh và sữa bắp thương hiệu Oh Fresh, phân phối qua siêu thị, minimart, tạp hóa, quán ăn và thương mại điện tử.",
        "gold_evidence": "với 2 sản phẩm nước tươi là sữa đậu xanh và sữa bắp thương hiệu Oh Fresh. Theo kế hoạch, các sản phẩm Oh Fresh đang và sẽ lần lượt được bày bán tại các hệ thống phân phối toàn quốc của Vinamilk và KIDO bao gồm: hệ thống các siêu thị, minimart, các điểm bán hàng tạp hóa, các quán ăn và trang thương mại điện tử.",
        "gold_page": 50,
        "gold_chunk_id": "vnm_p050_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_18",
        "category": "multi_hop",
        "question": "Theo báo cáo quản trị, trong Hội đồng Quản trị Vinamilk có những ai là thành viên độc lập?",
        "gold_answer": "Các thành viên HĐQT độc lập gồm có: Bà Lê Thị Băng Tâm, Bà Tiêu Yến Trinh và Ông Đỗ Lê Hùng.",
        "gold_evidence": "Các thành viên độc lập gồm có: Bà Lê Thị Băng Tâm, Bà Tiêu Yến Trinh và Ông Đỗ Lê Hùng.",
        "gold_page": 70,
        "gold_chunk_id": "vnm_p070_c03",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_19",
        "category": "multi_hop",
        "question": "Năm 2021, Vinamilk vươn lên xếp hạng thứ bao nhiêu trong top 50 công ty sữa hàng đầu thế giới về doanh thu?",
        "gold_answer": "Vinamilk vươn lên hạng 36 trong top 50 công ty sữa hàng đầu thế giới về doanh thu.",
        "gold_evidence": "vươn lên hạng 36 trong nhóm 50 các công ty sữa hàng đầu thế giới về doanh thu trong bảng xếp hạng năm 2021",
        "gold_page": 9,
        "gold_chunk_id": "vnm_p009_c01",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_20",
        "category": "multi_hop",
        "question": "Vinamilk quản lý và khai thác đàn bò với số lượng bao nhiêu con và có bao nhiêu trang trại bò sữa đạt chuẩn quốc tế tính đến 2021?",
        "gold_answer": "Quản lý khai thác đàn bò hơn 160.000 con cùng 14 trang trại bò sữa đạt chuẩn quốc tế.",
        "gold_evidence": "quản lý, khai thác đàn bò hơn 160.000 con cùng 14 trang trại bò sữa đạt chuẩn quốc tế",
        "gold_page": 9,
        "gold_chunk_id": "vnm_p009_c00",
        "split": "test",
        "type": "factual"
    },

    # Nhóm Text (4 câu)
    {
        "id": "adv_test_21",
        "category": "text",
        "question": "Vinamilk chính thức tăng tỷ lệ sở hữu vốn tại Công ty AngkorMilk ở Campuchia lên 100% vào năm nào?",
        "gold_answer": "Chính thức tăng tỷ lệ sở hữu vốn lên 100% vào năm 2017.",
        "gold_evidence": "chính thức tăng mức sở hữu vốn lên 100% vào năm 2017",
        "gold_page": 12,
        "gold_chunk_id": "vnm_p012_c02",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_22",
        "category": "text",
        "question": "Tính đến năm 2021, danh mục sản phẩm của Vinamilk gồm hơn bao nhiêu mặt hàng và được phủ khắp bao nhiêu tỉnh thành?",
        "gold_answer": "Danh mục sản phẩm trên 250 mặt hàng sữa và được phủ đều 63/63 tỉnh thành.",
        "gold_evidence": "Danh mục sản phẩm trên 250 mặt hàng sữa và các sản phẩm từ sữa của Vinamilk được phủ đều 63/63 tỉnh th ành.",
        "gold_page": 82,
        "gold_chunk_id": "vnm_p082_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_23",
        "category": "text",
        "question": "Hệ thống trang trại sinh thái nào của Vinamilk được ra đời trong năm 2021 để phát triển vùng nguyên liệu?",
        "gold_answer": "Hệ thống trang trại sinh thái Green Farm.",
        "gold_evidence": "sự ra đời Hệ thống trang trại sinh thái Green Farm",
        "gold_page": 4,
        "gold_chunk_id": "vnm_p004_c00",
        "split": "test",
        "type": "factual"
    },
    {
        "id": "adv_test_24",
        "category": "text",
        "question": "Đến năm 2021, tỷ lệ các sản phẩm là thực phẩm bổ sung chiếm bao nhiêu phần trăm trong danh mục của Vinamilk?",
        "gold_answer": "Chiếm hơn 50% danh mục sản phẩm.",
        "gold_evidence": ">50% danh mục sản phẩm là thực phẩm bổ sung.",
        "gold_page": 82,
        "gold_chunk_id": "vnm_p082_c00",
        "split": "test",
        "type": "factual"
    },

    # Nhóm Thiếu bằng chứng (6 câu)
    {
        "id": "adv_test_25",
        "category": "unanswerable",
        "question": "Chi phí mua bản quyền thương hiệu sữa chua Hy Lạp Chobani tại thị trường Mỹ của Vinamilk năm 2021 là bao nhiêu triệu USD?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không có thông tin về việc mua bản quyền thương hiệu Chobani.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    },
    {
        "id": "adv_test_26",
        "category": "unanswerable",
        "question": "Tên của phi công điều khiển trực thăng thị sát trang trại bò sữa Tây Ninh của Vinamilk vào ngày 15/08/2021 là ai?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 hoàn toàn không chứa thông tin về phi công thị sát trang trại.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    },
    {
        "id": "adv_test_27",
        "category": "unanswerable",
        "question": "Vinamilk đã nhập khẩu bao nhiêu tấn bơ lạt từ Argentina trong quý 2 năm 2021?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không có số liệu về sản lượng nhập khẩu bơ lạt từ Argentina trong quý 2 năm 2021.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    },
    {
        "id": "adv_test_28",
        "category": "unanswerable",
        "question": "Số lượng xe máy Honda Lead được tặng cho nhân viên xuất sắc nhất của Vinamilk trong tiệc tất niên 2021 là bao nhiêu chiếc?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không có thông tin về việc tặng xe máy Honda Lead.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    },
    {
        "id": "adv_test_29",
        "category": "unanswerable",
        "question": "Giá cước vận tải một container sữa 40 feet từ Cảng Cát Lái sang Cảng Thượng Hải trong tháng 10/2021 được Vinamilk chi trả là bao nhiêu USD?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không công bố chi tiết giá cước vận tải cụ thể cho từng container sang Thượng Hải.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    },
    {
        "id": "adv_test_30",
        "category": "unanswerable",
        "question": "Màu sắc đồng phục mới của nhân viên bán hàng tại chi nhánh Vinamilk Vientiane (Lào) trong năm 2025 là màu gì?",
        "gold_answer": "Tài liệu Báo cáo thường niên Vinamilk 2021 không có thông tin về màu đồng phục nhân viên tại Lào năm 2025.",
        "gold_evidence": "",
        "gold_page": 0,
        "gold_chunk_id": "",
        "split": "test",
        "type": "unanswerable"
    }
]

benchmark_data = {
    "metadata": {
        "title": "Vinamilk Annual Report 2021 Multimodal Benchmark",
        "source": "Báo cáo thường niên Vinamilk 2021 (121 trang)",
        "total_questions": len(dev_questions) + len(test_questions),
        "dev_count": len(dev_questions),
        "test_count": len(test_questions),
        "categories": {
            "table": sum(1 for q in test_questions if q['category'] == 'table'),
            "diagram": sum(1 for q in test_questions if q['category'] == 'diagram'),
            "chart": sum(1 for q in test_questions if q['category'] == 'chart'),
            "multi_hop": sum(1 for q in test_questions if q['category'] == 'multi_hop'),
            "text": sum(1 for q in test_questions if q['category'] == 'text'),
            "unanswerable": sum(1 for q in test_questions if q['category'] == 'unanswerable')
        }
    },
    "dev": dev_questions,
    "test": test_questions
}

BENCHMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(BENCHMARK_PATH, 'w', encoding='utf-8') as f:
    json.dump(benchmark_data, f, ensure_ascii=False, indent=2)

print(f"Generated Benchmark with {len(dev_questions)} Dev and {len(test_questions)} Test questions.")
print("Test category distribution:", benchmark_data["metadata"]["categories"])
