"""Agentic RAG Controller for Day 7 with Model Switching (OpenRouter, Groq)."""
import json
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from src.retrievers import HybridRetriever, Bm25Retriever, DenseRetriever
from src.embeddings import EmbeddingService

load_dotenv()

# Danh sách model hỗ trợ
SUPPORTED_MODELS = {
    "gemini-2.5-flash": {
        "provider": "openrouter",
        "model_id": "google/gemini-2.5-flash",
        "name": "Gemini 2.5 Flash (Google)"
    },
    "gemini-2.5-pro": {
        "provider": "openrouter",
        "model_id": "google/gemini-2.5-pro",
        "name": "Gemini 2.5 Pro (Google)"
    },
    "gpt-4o-mini": {
        "provider": "openrouter",
        "model_id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini (OpenAI)"
    },
    "llama-3.3-70b": {
        "provider": "openrouter",
        "model_id": "meta-llama/llama-3.3-70b-instruct",
        "name": "Llama 3.3 70B (Meta)"
    },
    "groq-qwen": {
        "provider": "groq",
        "model_id": "qwen/qwen3.8-27b",
        "name": "Qwen 3.8 27B (Groq)"
    }
}


class AgentController:
    def __init__(self, model_key: str = "gpt-4o-mini"):
        self.model_key = model_key if model_key in SUPPORTED_MODELS else "gpt-4o-mini"
        self.model_info = SUPPORTED_MODELS[self.model_key]
        self.client = self._init_client()

    def _init_client(self) -> OpenAI:
        provider = self.model_info["provider"]
        if provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        else:
            raise ValueError(f"Provider không hỗ trợ: {provider}")

    def switch_model(self, model_key: str):
        if model_key in SUPPORTED_MODELS:
            self.model_key = model_key
            self.model_info = SUPPORTED_MODELS[model_key]
            self.client = self._init_client()
            print(f"[AgentController] Đã chuyển sang model: {self.model_info['name']}")

    def decide_and_answer(self, question: str, context: str) -> dict:
        """LLM quyết định trả lời có trích dẫn hoặc từ chối nếu không đủ thông tin."""
        system_prompt = (
            "Bạn là trợ lý AI chuyên gia giải đáp Quy chế đào tạo và Công tác sinh viên dựa trên Sổ tay sinh viên K67.\n"
            "NGUYÊN TẮC BẮT BUỘC:\n"
            "1. CHỈ sử dụng thông tin trong phần [BẰNG CHỨNG TÀI LIỆU] được cung cấp dưới đây để trả lời.\n"
            "2. Khi trả lời, phải trích dẫn rõ mã chunk hoặc trang nguồn trong ngoặc vuông, ví dụ: [so_tay_sinh_vien_k67_p018_2] hoặc [Trang 18].\n"
            "3. Nếu phần [BẰNG CHỨNG TÀI LIỆU] KHÔNG có thông tin hoặc không đủ cơ sở để khẳng định, bạn BẮT BUỘC PHẢI TỪ CHỐI (ABSTAIN) bằng câu:\n"
            "   'Tài liệu Sổ tay sinh viên K67 không cung cấp thông tin về [chủ đề câu hỏi].'\n"
            "   Tuyệt đối KHÔNG ĐƯỢC bịa đặt, suy đoán hay sử dụng kiến thức ngoài tài liệu.\n"
            "4. Định dạng phản hồi JSON duy nhất theo schema sau:\n"
            "{\n"
            "  \"status\": \"answered\" HOẶC \"abstain\",\n"
            "  \"answer\": \"Nội dung câu trả lời hoặc câu từ chối\",\n"
            "  \"citations\": [\"chunk_id_1\", \"chunk_id_2\"],\n"
            "  \"reasoning\": \"Giải thích ngắn gọn căn cứ\"\n"
            "}"
        )

        user_content = (
            f"CÂU HỎI: {question}\n\n"
            f"[BẰNG CHỨNG TÀI LIỆU]:\n{context if context.strip() else '(Không có bằng chứng nào)'}"
        )

        for attempt in range(2):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_info["model_id"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                    max_tokens=600
                )
                text = resp.choices[0].message.content.strip()
                data = json.loads(text)
                return {
                    "status": data.get("status", "answered"),
                    "answer": data.get("answer", ""),
                    "citations": data.get("citations", []),
                    "reasoning": data.get("reasoning", "")
                }
            except Exception as e:
                if attempt == 1:
                    return {
                        "status": "error",
                        "answer": f"Lỗi gọi LLM: {e}",
                        "citations": [],
                        "reasoning": "Exception occurred"
                    }
                time.sleep(1)


class AgenticRAG:
    """Agentic RAG Engine combining Retriever and LLM Controller."""
    def __init__(self, retriever=None, model_key: str = "gpt-4o-mini", context_budget: int = 1500, top_k: int = 5):
        self.chunks_file = Path("data/chunks.json")
        self.chunks = json.load(open(self.chunks_file, encoding="utf-8"))
        
        # Mặc định sử dụng Hybrid Retriever tối ưu nhất
        if retriever is None:
            embed_service = EmbeddingService()
            dense = DenseRetriever(self.chunks, embedding_service=embed_service, use_db=False)
            bm25 = Bm25Retriever(self.chunks)
            self.retriever = HybridRetriever(dense, bm25, rrf_k=60)
        else:
            self.retriever = retriever

        self.controller = AgentController(model_key=model_key)
        self.context_budget = context_budget
        self.top_k = top_k

    def run(self, question: str, filter_meta: dict | None = None) -> dict:
        """Run full agentic cycle: search -> pack context -> reason & answer."""
        start_time = time.perf_counter()
        events = []

        # Bước 1: Tool Call - Retrieval
        events.append({"event": "thought", "detail": f"Khởi tạo tìm kiếm bằng chứng cho câu hỏi: '{question}'"})
        retrieval_start = time.perf_counter()
        results = self.retriever.search(question, top_k=self.top_k, filter_meta=filter_meta)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        events.append({
            "event": "tool_call",
            "tool": "search",
            "params": {"query": question, "top_k": self.top_k, "filter": filter_meta},
            "retrieved_count": len(results),
            "top_candidates": [{"id": r["id"], "page": r["page"], "score": round(r.get("score", 0), 4)} for r in results],
            "elapsed_ms": round(retrieval_ms, 2)
        })

        # Bước 2: Pack Context theo Budget
        blocks, context_ids = [], []
        for c in results:
            block = f"[{c['id']} | Trang {c['page']}]\n{c['text']}"
            candidate = "\n\n".join(blocks + [block])
            if len(candidate) <= self.context_budget:
                blocks.append(block)
                context_ids.append(c["id"])
            elif not blocks:
                blocks.append(block[:self.context_budget])
                context_ids.append(c["id"])
                break

        final_context = "\n\n".join(blocks)
        events.append({
            "event": "context_packed",
            "context_ids": context_ids,
            "char_count": len(final_context),
            "budget": self.context_budget
        })

        # Bước 3: Controller Reasoning & Synthesis
        decision = self.controller.decide_and_answer(question, final_context)
        total_ms = (time.perf_counter() - start_time) * 1000

        # Kiểm tra tính hợp lệ của citations: phải nằm trong context_ids
        valid_citations = [cid for cid in decision.get("citations", []) if any(cid in ctx_id for ctx_id in context_ids)]

        events.append({
            "event": "decision",
            "status": decision.get("status"),
            "citations_returned": decision.get("citations"),
            "valid_citations": valid_citations
        })

        retriever_display = getattr(self.retriever, "name", "Hybrid (Dense + BM25 RRF)")

        return {
            "question": question,
            "status": decision.get("status"),
            "answer": decision.get("answer"),
            "citations": decision.get("citations"),
            "valid_citations": valid_citations,
            "reasoning": decision.get("reasoning"),
            "context": final_context,
            "context_ids": context_ids,
            "model_used": self.controller.model_info["name"],
            "retriever_used": retriever_display,
            "events": events,
            "elapsed_ms": round(total_ms, 2)
        }
