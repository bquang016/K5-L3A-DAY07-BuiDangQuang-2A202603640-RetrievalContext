"""High-performance Lightweight Web Server for Agentic RAG Interactive Dashboard."""
import http.server
import json
import os
import socketserver
import sys
import urllib.parse
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent
ROOT_DIR = UI_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent import AgenticRAG, SUPPORTED_MODELS
from src.retrievers import Bm25Retriever, DenseRetriever, HybridRetriever
from src.embeddings import EmbeddingService

PORT = 8083

# Cache sẵn retrievers để UI phản hồi tức thì
print("[Web Server] Đang tải dữ liệu và khởi tạo Retrievers...")
chunks = json.load(open(ROOT_DIR / "data/chunks.json", encoding="utf-8"))
embed_service = EmbeddingService()
dense_retriever = DenseRetriever(chunks, embedding_service=embed_service, use_db=False)
bm25_retriever = Bm25Retriever(chunks)
hybrid_retriever = HybridRetriever(dense_retriever, bm25_retriever, rrf_k=60)

# Khởi tạo Agent
rag_agent = AgenticRAG(retriever=hybrid_retriever, model_key="gemini-2.5-flash", context_budget=1500, top_k=5)
print("[Web Server] Sẵn sàng phục vụ!")


class AgenticHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
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
            questions = json.load(open(ROOT_DIR / "data/benchmark_questions.json", encoding="utf-8"))
            samples = [
                {"id": q["id"], "question": q["question"], "answerable": q.get("answerable", True), "split": q.get("split")}
                for q in questions[:16]
            ]
            self.wfile.write(json.dumps(samples, ensure_ascii=False).encode("utf-8"))
            return

        elif url.path == "/api/benchmark_data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
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
            model_key = req.get("model", "gpt-4o-mini")
            retriever_type = req.get("retriever", "hybrid")
            budget = int(req.get("budget", 1500))
            top_k = int(req.get("top_k", 5))

            if not question:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Question is empty"}')
                return

            # Cấu hình dynamic theo request
            if retriever_type == "bm25":
                rag_agent.retriever = bm25_retriever
            elif retriever_type == "dense":
                rag_agent.retriever = dense_retriever
            else:
                rag_agent.retriever = hybrid_retriever

            print(f"[Web Server] Request chat: model={model_key} | retriever_req={retriever_type} -> active: {rag_agent.retriever.name}")

            rag_agent.context_budget = budget
            rag_agent.top_k = top_k
            rag_agent.controller.switch_model(model_key)

            # Chạy Agentic cycle
            response = rag_agent.run(question)

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
