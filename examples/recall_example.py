#!/usr/bin/env python3
"""
记忆召回示例
演示如何调用 memory-tdai 的召回接口
"""

import requests
import json

EMBEDDING_API = "http://localhost:8080/v1/embeddings"
MEMORY_DB = "~/.openclaw/memory-tencentdb/memories"

def generate_embedding(text: str) -> list[float]:
    """调用本地 embedding 服务生成向量"""
    response = requests.post(
        EMBEDDING_API,
        json={"input": text}
    )
    data = response.json()
    return data["data"][0]["embedding"]

def search_memories(query: str, top_k: int = 5) -> list[dict]:
    """
    搜索相关记忆

    实际项目中通过 memory-tdai 的 recall 机制自动调用
    这里演示手动实现思路
    """
    # 1. 生成查询向量
    query_vec = generate_embedding(query)

    # 2. 这里应该调用 memory-tdai 的召回接口
    # 实际使用时只需在 Agent 中配置 recall.enabled = true
    # 系统会自动处理召回逻辑

    # 3. 模拟返回结果
    print(f"查询: {query}")
    print(f"向量维度: {len(query_vec)}")
    print(f"Top-{top_k} 结果将在 Agent 对话时自动返回")

    return []

def demo_recall_flow():
    """演示完整召回流程"""
    print("=== 记忆召回演示 ===\n")

    queries = [
        "我之前问过你关于什么 AI 框架的问题？",
        "我的 OpenClaw 配置是什么样的？",
        "我感兴趣的技术领域有哪些？"
    ]

    for q in queries:
        search_memories(q)
        print()

if __name__ == "__main__":
    demo_recall_flow()