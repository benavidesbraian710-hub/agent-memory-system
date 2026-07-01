"""
Memory API Client
外部 Agent 调用记忆服务的客户端示例
"""

import requests
from typing import Optional

class MemoryClient:
    """记忆服务客户端"""

    def __init__(self, base_url: str = "http://localhost:18790"):
        self.base_url = base_url

    def add_memory(self, content: str, keywords: list[str] = None,
                   session_id: str = None) -> str:
        """添加记忆，返回 memory_id"""
        resp = requests.post(
            f"{self.base_url}/memory",
            json={
                "content": content,
                "keywords": keywords or [],
                "session_id": session_id
            }
        )
        resp.raise_for_status()
        return resp.json()["memory_id"]

    def recall(self, query: str, strategy: str = "hybrid", top_k: int = 5) -> list[dict]:
        """召回相关记忆"""
        resp = requests.post(
            f"{self.base_url}/recall",
            json={
                "query": query,
                "strategy": strategy,
                "top_k": top_k
            }
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def add_session(self, session_id: str, messages: list[dict]) -> bool:
        """添加会话"""
        resp = requests.post(
            f"{self.base_url}/session",
            json={
                "session_id": session_id,
                "messages": messages
            }
        )
        resp.raise_for_status()
        return True

    def get_stats(self) -> dict:
        """获取统计"""
        resp = requests.get(f"{self.base_url}/stats")
        resp.raise_for_status()
        return resp.json()


# ============ 使用示例 ============

if __name__ == "__main__":
    client = MemoryClient()

    # 添加记忆
    memory_id = client.add_memory(
        content="用户对 AI Agent 框架感兴趣，特别是 OpenClaw",
        keywords=["AI", "OpenClaw", "Agent"]
    )
    print(f"添加记忆: {memory_id}")

    # 召回
    results = client.recall("用户喜欢什么技术？")
    print(f"召回结果: {results}")

    # 统计
    stats = client.get_stats()
    print(f"统计: {stats}")