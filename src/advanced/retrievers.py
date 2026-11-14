import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter

class BM25Okapi:
    def __init__(self, corpus: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_lens = []
        self.doc_freqs = Counter()
        self.docs = []
        
        total_len = 0
        for doc in corpus:
            tokens = self.tokenize(doc["text"])
            self.docs.append(tokens)
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_len += doc_len
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
                
        self.num_docs = len(corpus)
        self.avg_doc_len = total_len / self.num_docs if self.num_docs > 0 else 0
        self.idf = {}
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log((self.num_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            
    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        return re.findall(r'\b\w+\b', text)
        
    def score(self, query_tokens: List[str], doc_idx: int) -> float:
        score = 0.0
        doc_tokens = self.docs[doc_idx]
        doc_len = self.doc_lens[doc_idx]
        counts = Counter(doc_tokens)
        
        for q in query_tokens:
            if q not in self.idf:
                continue
            tf = counts[q]
            idf = self.idf[q]
            denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
            score += idf * (tf * (self.k1 + 1.0)) / denom if denom > 0 else 0
        return score

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        tokens = self.tokenize(query)
        scores = []
        for idx, doc in enumerate(self.corpus):
            s = self.score(tokens, idx)
            scores.append((idx, s))
            
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, s in scores[:top_k]:
            doc_copy = dict(self.corpus[idx])
            doc_copy["score"] = round(s, 4)
            results.append(doc_copy)
        return results

class AdvancedHybridRetriever:
    def __init__(self, corpus: List[Dict[str, Any]], rrf_k: int = 60):
        self.corpus = corpus
        self.bm25 = BM25Okapi(corpus)
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 8, content_type_hint: Optional[str] = None) -> List[Dict[str, Any]]:
        bm25_candidates = self.bm25.search(query, top_k=30)
        
        query_words = re.findall(r'\b\w+\b', query.lower())
        special_keywords = {'ebitda', 'roa', 'roe', 'eps', 'băng tâm', 'mai hoài anh', 'miraka', 'vibev', 'angkor', 'green farm'}
        query_specials = [w for w in query_words if w in special_keywords]
        
        boosted_scores = {}
        for rank, doc in enumerate(bm25_candidates):
            cid = doc["id"]
            rrf_score = 1.0 / (self.rrf_k + rank + 1)
            doc_text_lower = doc["text"].lower()
            
            # Boost mạnh cho các thuật ngữ viết tắt và thực thể riêng
            for sp in query_specials:
                if sp in doc_text_lower:
                    rrf_score += 0.05
                    
            # Khớp năm hoặc số liệu cụ thể
            for w in query_words:
                if re.match(r'^\d{4}$', w) and w in doc_text_lower:
                    rrf_score += 0.008
                    
            boosted_scores[cid] = (doc, rrf_score)
            
        ranked = sorted(boosted_scores.values(), key=lambda x: x[1], reverse=True)
        results = []
        for doc, score in ranked[:top_k]:
            item = dict(doc)
            item["score"] = round(score, 6)
            results.append(item)
        return results
