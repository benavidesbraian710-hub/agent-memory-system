"""
Embedding Engine - 向量化引擎
支持本地模型和远程 API
"""

import os
import json
import requests
from typing import Union

class EmbeddingEngine:
    """向量化引擎，支持多种 provider"""

    def __init__(self, config: dict = None):
        """
        config: {
            "provider": "openai|local|siliconflow",
            "model": "bge-small-zh-v1.5",
            "baseUrl": "http://localhost:8080/v1",
            "apiKey": "xxx",
            "dimensions": 512
        }
        """
        self.config = config or {}
        self.provider = self.config.get("provider", "openai")
        self.model = self.config.get("model", "bge-small-zh-v1.5")
        self.dimensions = self.config.get("dimensions", 512)
        self.base_url = self.config.get("baseUrl", "http://localhost:8080/v1")
        self.api_key = self.config.get("apiKey", "no-key")

        if self.provider == "local":
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer(self.model)

    def encode(self, texts: Union[str, list[str]]) -> list[list[float]]:
        """
        将文本转换为向量
        texts: 单个文本或文本列表
        返回: 向量列表
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.provider == "local":
            return self._encode_local(texts)
        else:
            return self._encode_api(texts)

    def _encode_local(self, texts: list[str]) -> list[list[float]]:
        """使用本地模型"""
        embeddings = self._local_model.encode(texts)
        return embeddings.tolist()

    def _encode_api(self, texts: list[str]) -> list[list[float]]:
        """使用远程 API"""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"input": texts, "model": self.model}

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        return [item["embedding"] for item in data["data"]]

    def similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """计算两个向量的余弦相似度"""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot / (norm1 * norm2 + 1e-9)