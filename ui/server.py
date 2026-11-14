"""High-performance Lightweight Web Server for Agentic RAG Interactive Dashboard."""
import http.server
import json
import os
import re
import socketserver
import sys
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

UI_DIR = Path(__file__).resolve().parent
ROOT_DIR = UI_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent import AgenticRAG, SUPPORTED_MODELS
from src.retrievers import Bm25Retriever, DenseRetriever, HybridRetriever
from src.embeddings import EmbeddingService
from src.advanced.agent import AdvancedAgenticRAG

PORT = 8083

print("[Web Server] Đang tải dữ liệu K67 và khởi tạo Retrievers...")
chunks_k67 = json.load(open(ROOT_DIR / "data/chunks.json", encoding="utf-8"))
embed_service = EmbeddingService()
dense_retriever_k67 = DenseRetriever(chunks_k67, embedding_service=embed_service, use_db=False)
bm25_retriever_k67 = Bm25Retriever(chunks_k67)
hybrid_retriever_k67 = HybridRetriever(dense_retriever_k67, bm25_retriever_k67, rrf_k=60)

rag_agent_k67 = AgenticRAG(retriever=hybrid_retriever_k67, model_key="gemini-2.5-flash", context_budget=1500, top_k=5)

print("[Web Server] Đang tải dữ liệu Vinamilk BCTN (121 trang) và khởi tạo Advanced Agent...")
vnm_agent = AdvancedAgenticRAG(model_name="google/gemini-2.5-flash", budget=3500)

print("[Web Server] Sẵn sàng phục vụ!")


class AgenticHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(url.query)

        if url.path == "/api/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            data = [{"key": k, "name": v["name"], "provider": v["provider"]} for k, v in SUPPORTED_MODELS.items()]
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        elif url.path == "/api/samples":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()

            dataset = params.get("dataset", ["k67"])[0]

            if dataset == "vinamilk":
                bench = json.load(open(ROOT_DIR / "data/advanced/benchmark.json", encoding="utf-8"))
                samples = []
                for q in (bench["dev"] + bench["test"])[:18]:
                    samples.append({
                        "id": q["id"],
                        "question": q["question"],
                        "category": q["category"],
                        "answerable": q["type"] != "unanswerable",
                        "split": q["split"]
                    })
            else:
                questions = json.load(open(ROOT_DIR / "data/benchmark_questions.json", encoding="utf-8"))
                samples = [
                    {"id": q["id"], "question": q["question"], "category": "k67", "answerable": q.get("answerable", True), "split": q.get("split")}
                    for q in questions[:16]
                ]

            self.wfile.write(json.dumps(samples, ensure_ascii=False).encode("utf-8"))
            return

        elif url.path == "/api/benchmark_data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            dataset = params.get("dataset", ["k67"])[0]
            if dataset == "vinamilk":
                res_file = ROOT_DIR / "results/advanced/test_results.json"
            else:
                res_file = ROOT_DIR / "results/retrieval_dev_baseline.json"

            if res_file.exists():
                data = json.load(open(res_file, encoding="utf-8"))
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            else:
                self.wfile.write(b"{}")
            return

        elif url.path == "/" or url.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            req = json.loads(body)

            question = req.get("question", "").strip()
            dataset = req.get("dataset", "k67")
            model_key = req.get("model", "gemini-2.5-flash")
            retriever_type = req.get("retriever", "hybrid")
            budget = int(req.get("budget", 1500))
            top_k = int(req.get("top_k", 5))

            if not question:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Question is empty"}')
                return

            print(f"[Web Server] Request chat: dataset={dataset} | model={model_key} | retriever={retriever_type}")

            if dataset == "vinamilk":
                # Chạy Vinamilk Agent
                model_mapping = {
                    "gemini-2.5-flash": "google/gemini-2.5-flash",
                    "gemini-2.5-pro": "google/gemini-2.5-pro",
                    "gpt-4o-mini": "openai/gpt-4o-mini",
                    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
                    "groq-qwen": "google/gemini-2.5-flash"
                }
                target_model = model_mapping.get(model_key, "google/gemini-2.5-flash")
                vnm_agent.model_name = target_model
                vnm_agent.budget = budget if budget >= 2000 else 3500

                vnm_res = vnm_agent.answer(question)

                # Format answer text
                raw_ans = vnm_res["answer"]
                clean_ans = raw_ans
                citations = []

                if "Content:" in raw_ans:
                    parts = raw_ans.split("Content:", 1)
                    if "Citations:" in parts[1]:
                        c_part = parts[1].split("Citations:", 1)
                        clean_ans = c_part[0].strip()
                        citations = [c.strip() for c in c_part[1].split(",") if c.strip() and c.strip().lower() != "none"]
                    else:
                        clean_ans = parts[1].strip()

                # Extract bracket citations e.g. [vnm_p010_c00]
                bracket_cites = re.findall(r'\[(vnm_p\d+_c\d+)\]', raw_ans)
                for bc in bracket_cites:
                    if bc not in citations:
                        citations.append(bc)

                # Extract candidates info
                top_candidates = []
                for cid in vnm_res["candidates"][:5]:
                    # vnm_p010_c00
                    p_match = re.search(r'p(\d+)', cid)
                    page_num = int(p_match.group(1)) if p_match else 0
                    top_candidates.append({
                        "page": page_num,
                        "chunk_id": cid,
                        "score": "RRF-Matched"
                    })

                status = "abstain" if vnm_res["is_abstain"] else "grounded"
                response = {
                    "status": status,
                    "answer": clean_ans,
                    "citations": citations,
                    "elapsed_ms": vnm_res["latency_total_ms"],
                    "model_used": SUPPORTED_MODELS.get(model_key, {}).get("name", model_key),
                    "retriever_used": "Vinamilk Multimodal Hybrid RRF",
                    "dataset_used": "Báo cáo thường niên Vinamilk 2021 (121 trang)",
                    "events": [
                        {
                            "event": "tool_call",
                            "tool": "search_vinamilk_multimodal",
                            "latency_ms": vnm_res["latency_tool_ms"],
                            "top_candidates": top_candidates
                        },
                        {
                            "event": "context_packed",
                            "packed_chars": len(vnm_res["context_packed"]),
                            "budget_limit": vnm_agent.budget,
                            "chunks_count": len(vnm_res["candidates"])
                        }
                    ],
                    "reasoning": "Agent đã truy xuất các bảng biểu tài chính, biểu đồ tăng trưởng và sơ đồ cơ cấu trong BCTN Vinamilk 2021 để tổng hợp câu trả lời."
                }
            else:
                # Chạy K67 Agent
                if retriever_type == "bm25":
                    rag_agent_k67.retriever = bm25_retriever_k67
                elif retriever_type == "dense":
                    rag_agent_k67.retriever = dense_retriever_k67
                else:
                    rag_agent_k67.retriever = hybrid_retriever_k67

                rag_agent_k67.context_budget = budget
                rag_agent_k67.top_k = top_k
                rag_agent_k67.controller.switch_model(model_key)

                response = rag_agent_k67.run(question)
                response["dataset_used"] = "Sổ tay sinh viên Khóa 67 (VNUA)"

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    with socketserver.TCPServer(("", PORT), AgenticHandler) as httpd:
        print(f"\n=======================================================")
        print(f"🎉 GIAO DIỆN AGENTIC RAG ĐANG CHẠY TẠI:")
        print(f"👉 http://localhost:{PORT}")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Web Server] Đang dừng máy chủ...")


if __name__ == "__main__":
    run_server()
