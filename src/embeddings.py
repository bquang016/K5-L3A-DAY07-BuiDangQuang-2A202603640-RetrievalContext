"""Embedding service with disk caching for Day 7, inheriting 100% from Day 6."""
import hashlib
import json
import math
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path("artifacts")
CACHE_FILE = CACHE_DIR / "embedding_cache.json"
DAY6_CACHE = Path(r"C:\Users\buida\K5-L3A-DAY06-BuiDangQuang-2A202603640-DataIngestion\artifacts\embedding_cache.json")


class EmbeddingService:
    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.cache: dict[str, list[float]] = {}
        self.client = None
        self._load_cache()

    def _init_client(self):
        if self.client is None and self.api_key:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )

    def _load_cache(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # 1. Thử nạp từ Day 6 nếu có quyền
        try:
            if DAY6_CACHE.exists():
                with open(DAY6_CACHE, "r", encoding="utf-8") as f:
                    day6_data = json.load(f)
                    self.cache.update(day6_data)
                    print(f"[EmbeddingService] Đã kế thừa {len(day6_data)} embeddings từ Day 6 cache.")
        except Exception:
            pass

        # 2. Nạp từ cache nội bộ Day 7
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    local_data = json.load(f)
                    self.cache.update(local_data)
                    print(f"[EmbeddingService] Đã nạp {len(local_data)} embeddings từ Day 7 cache.")
            except Exception as e:
                print(f"[EmbeddingService] Không thể đọc cache Day 7: {e}")

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"[EmbeddingService] Lỗi lưu cache: {e}")

    def _hash(self, text: str) -> str:
        # Giữ chuẩn hash y hệt Day 6: {model_name}:{text}
        key = f"{self.model_name}:{text}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def get_embedding(self, text: str) -> list[float]:
        h = self._hash(text)
        if h in self.cache:
            return self.cache[h]

        self._init_client()
        if not self.client:
            raise ValueError("Không tìm thấy OPENROUTER_API_KEY để gọi OpenRouter!")

        for attempt in range(3):
            try:
                resp = self.client.embeddings.create(
                    model=self.model_name,
                    input=[text]
                )
                vec = resp.data[0].embedding
                self.cache[h] = vec
                self._save_cache()
                return vec
            except Exception as e:
                if attempt == 2:
                    raise RuntimeError(f"Lỗi gọi Embedding API OpenRouter qua OpenAI client sau 3 lần thử: {e}")
                time.sleep(1.5)
        return []

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        missing_indices = []
        results = [None] * len(texts)

        for i, t in enumerate(texts):
            h = self._hash(t)
            if h in self.cache:
                results[i] = self.cache[h]
            else:
                missing_indices.append(i)

        if not missing_indices:
            return results

        print(f"[EmbeddingService] Cần gọi API nhúng mới {len(missing_indices)} texts...")
        self._init_client()
        
        batch_size = 20
        for b_start in range(0, len(missing_indices), batch_size):
            b_sub = missing_indices[b_start:b_start + batch_size]
            b_texts = [texts[idx] for idx in b_sub]

            resp = self.client.embeddings.create(
                model=self.model_name,
                input=b_texts
            )
            for idx, item in zip(b_sub, resp.data):
                vec = item.embedding
                results[idx] = vec
                self.cache[self._hash(texts[idx])] = vec
            time.sleep(0.3)

        self._save_cache()
        return results


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)
