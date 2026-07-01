"""
Recall Engine - 召回引擎
RRF 融合多路召回
"""

from typing import list
from .storage import MemoryStorage
from .embedding import EmbeddingEngine

class RecallEngine:
    """混合召回引擎"""

    def __init__(self, storage: MemoryStorage, embedding: EmbeddingEngine, config: dict = None):
        self.storage = storage
        self.embedding = embedding
        self.config = config or {}
        self.max_results = self.config.get("maxResults", 5)
        self.threshold = self.config.get("scoreThreshold", 0.3)

    def recall(self, query: str, strategy: str = "hybrid", top_k: int = None) -> list[dict]:
        """
        召回相关记忆
        query: 查询文本
        strategy: "keyword" | "embedding" | "hybrid"
        """
        top_k = top_k or self.max_results

        if strategy == "keyword":
            return self._keyword_recall(query, top_k)
        elif strategy == "embedding":
            return self._embedding_recall(query, top_k)
        else:  # hybrid
            return self._hybrid_recall(query, top_k)

    def _keyword_recall(self, query: str, top_k: int) -> list[dict]:
        """纯关键词召回"""
        results = self.storage.search_keyword(query, top_k * 2)
        for r in results:
            r["score"] = 1.0  # 关键词匹配满分
        return results[:top_k]

    def _embedding_recall(self, query: str, top_k: int) -> list[dict]:
        """纯向量召回"""
        query_vec = self.embedding.encode(query)[0]
        results = self.storage.search_similar(query_vec, top_k * 2, self.threshold)
        for r in results:
            r["score"] = r.pop("similarity", 0)
        return results[:top_k]

    def _hybrid_recall(self, query: str, top_k: int) -> list[dict]:
        """RRF 混合召回"""
        k = 60  # RRF 参数

        # 并行两路召回
        keyword_results = self._keyword_recall(query, top_k * 2)
        embedding_results = self._embedding_recall(query, top_k * 2)

        # 构建排名表
        scores = {}

        for rank, item in enumerate(keyword_results):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank + 1)
            item["keyword_rank"] = rank

        for rank, item in enumerate(embedding_results):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank + 1)
            item["embedding_rank"] = rank

        # 合并结果
        all_items = {item["id"]: item for item in keyword_results + embedding_results}
        for item_id, score in scores.items():
            all_items[item_id]["rrf_score"] = score

        # 排序
        sorted_results = sorted(all_items.values(), key=lambda x: x["rrf_score"], reverse=True)

        # 过滤阈值
        filtered = [r for r in sorted_results if r["rrf_score"] >= self.threshold * k / (k + 1)]

        return filtered[:top_k]

    def dedup(self, new_content: str, new_embedding: list[float],
              existing_contents: list[str], threshold: float = 0.9) -> bool:
        """
        检查是否与已有记忆重复
        返回 True 表示重复，False 表示不重复
        """
        for content in existing_contents:
            existing_vec = self.embedding.encode(content)[0]
            sim = self.embedding.similarity(new_embedding, existing_vec)
            if sim >= threshold:
                return True
        return False