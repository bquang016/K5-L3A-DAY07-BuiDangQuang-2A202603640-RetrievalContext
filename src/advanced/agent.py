import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from openai import OpenAI
from src.advanced.retrievers import AdvancedHybridRetriever

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class AdvancedAgenticRAG:
    def __init__(self, model_name: str = "google/gemini-2.5-flash", budget: int = 3500):
        self.model_name = model_name
        self.budget = budget
        
        # Load chunks
        chunks_path = ROOT_DIR / "data" / "advanced" / "chunks.json"
        with open(chunks_path, encoding='utf-8') as f:
            self.corpus = json.load(f)
            
        self.retriever = AdvancedHybridRetriever(self.corpus)
        
        # OpenRouter client
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    def pack_context(self, candidates: List[Dict[str, Any]]) -> str:
        current_len = 0
        packed = []
        for doc in candidates:
            chunk_str = f"[{doc['id']} - Trang {doc['page']} ({doc['content_type']})]\n{doc['text']}\n"
            if current_len + len(chunk_str) <= self.budget:
                packed.append(chunk_str)
                current_len += len(chunk_str)
            elif not packed:
                packed.append(chunk_str[:self.budget])
                break
        return "\n".join(packed)

    def answer(self, query: str, content_type_hint: Optional[str] = None) -> Dict[str, Any]:
        t0 = time.perf_counter()
        
        # Retrieve top 8 candidates with entity boosting
        candidates = self.retriever.search(query, top_k=8, content_type_hint=content_type_hint)
        t_tool = time.perf_counter()
        
        context_packed = self.pack_context(candidates)
        
        system_prompt = (
            "Bạn là chuyên gia phân tích dữ liệu Báo cáo thường niên Vinamilk 2021.\n"
            "NGUYÊN TẮC BẮT BUỘC:\n"
            "1. Đọc kỹ toàn bộ [BẰNG CHỨNG TÀI LIỆU] được cung cấp để trả lời đúng, đầy đủ các ý, tên tổ chức và số liệu được hỏi.\n"
            "2. Trích dẫn rõ ràng mã chunk trong ngoặc vuông, ví dụ [vnm_p010_c00] hoặc số trang [Trang 10].\n"
            "3. Nếu tài liệu hoàn toàn không có thông tin hoặc câu hỏi là điều bịa đặt không có thật, bạn PHẢI TỪ CHỐI (ABSTAIN) bằng câu: "
            "'Tài liệu Báo cáo thường niên Vinamilk 2021 không cung cấp thông tin về [chủ đề câu hỏi].' Tuyệt đối không suy đoán.\n"
            "4. Định dạng trả lời:\n"
            "Status: [ANSWER / ABSTAIN]\n"
            "Content: <Nội dung trả lời chi tiết kèm trích dẫn nguồn, hoặc câu từ chối chuẩn mực>\n"
            "Citations: <Các mã chunk nguồn liên quan>"
        )

        user_prompt = f"[BẰNG CHỨNG TÀI LIỆU]:\n{context_packed}\n\n[CÂU HỎI]: {query}"
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=600
            )
            raw_answer = resp.choices[0].message.content or ""
        except Exception as e:
            raw_answer = f"Status: ERROR\nContent: Lỗi gọi mô hình: {e}\nCitations: none"
            
        t_total = time.perf_counter()
        
        is_abstain = "ABSTAIN" in raw_answer.upper() or "không cung cấp thông tin" in raw_answer.lower()
        
        return {
            "query": query,
            "answer": raw_answer,
            "is_abstain": is_abstain,
            "candidates": [c["id"] for c in candidates],
            "context_packed": context_packed,
            "latency_tool_ms": round((t_tool - t0) * 1000, 2),
            "latency_total_ms": round((t_total - t0) * 1000, 2)
        }
