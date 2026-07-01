"""
Memory Service - 记忆服务主类
统一接口，对外暴露
"""

import json
import uuid
from datetime import datetime
from typing import Optional
from .storage import MemoryStorage
from .embedding import EmbeddingEngine
from .recall import RecallEngine

class MemoryService:
    """
    统一记忆服务接口

    用法:
        service = MemoryService()
        service.add_memory("用户喜欢 OpenClaw", session_id="sess_123")
        results = service.recall("用户偏好什么框架？")
    """

    def __init__(self, config: dict = None):
        """
        config: {
            "db_path": "~/.agent-memory/memory.db",
            "embedding": {
                "provider": "openai|local",
                "model": "bge-small-zh-v1.5",
                "baseUrl": "http://localhost:8080/v1",
                "dimensions": 512
            },
            "recall": {
                "maxResults": 5,
                "scoreThreshold": 0.3,
                "strategy": "hybrid"
            }
        }
        """
        self.config = config or {}

        # 初始化各组件
        db_path = self.config.get("db_path")
        self.storage = MemoryStorage(db_path)

        emb_config = self.config.get("embedding", {})
        self.embedding = EmbeddingEngine(emb_config)

        recall_config = self.config.get("recall", {})
        self.recall = RecallEngine(self.storage, self.embedding, recall_config)

    def add_memory(self, content: str, keywords: list[str] = None,
                   session_id: str = None, metadata: dict = None,
                   layer: str = "L1", auto_dedup: bool = True) -> str:
        """
        添加记忆
        返回 memory_id
        """
        # 生成向量
        embedding = self.embedding.encode(content)[0]

        # 去重检查
        if auto_dedup and layer == "L1":
            existing = self.storage.search_keyword(keywords[0] if keywords else content, top_k=10)
            existing_contents = [m["content"] for m in existing]
            if self.recall.dedup(content, embedding, existing_contents):
                # 找到相似记忆，更新而非添加
                return existing[0]["id"]

        # 添加记忆
        memory_id = self.storage.add_memory(
            content=content,
            embedding=embedding,
            keywords=keywords,
            session_id=session_id,
            metadata=metadata,
            layer=layer
        )
        return memory_id

    def recall(self, query: str, strategy: str = "hybrid", top_k: int = None) -> list[dict]:
        """
        召回相关记忆
        返回记忆列表，按相关性排序
        """
        return self.recall.recall(query, strategy, top_k)

    def add_session(self, session_id: str, messages: list[dict], metadata: dict = None):
        """添加会话"""
        self.storage.add_session(session_id, messages, metadata)

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话"""
        return self.storage.get_session(session_id)

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.storage.get_stats()

    def extract_from_conversation(self, messages: list[dict],
                                  session_id: str = None) -> list[str]:
        """
        从对话中提取记忆（需要 LLM，这里是简化版）
        实际使用时需要调用 LLM API 进行提取
        """
        # 简化实现：提取关键实体
        # 正式实现应该调用 LLM 分析对话
        memory_ids = []

        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if len(content) > 10:
                    # 简化：直接添加用户消息作为记忆
                    memory_id = self.add_memory(
                        content=content,
                        session_id=session_id,
                        layer="L1"
                    )
                    memory_ids.append(memory_id)

        return memory_ids

    @staticmethod
    def create_default_config() -> dict:
        """创建默认配置"""
        return {
            "db_path": "~/.agent-memory/memory.db",
            "embedding": {
                "provider": "local",
                "model": "BAAI/bge-small-zh-v1.5",
                "dimensions": 512
            },
            "recall": {
                "maxResults": 5,
                "scoreThreshold": 0.3,
                "strategy": "hybrid"
            }
        }