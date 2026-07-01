"""
使用示例 - 独立模式
不依赖 OpenClaw，直接使用 MemoryService
"""

import sys
sys.path.insert(0, "..")

from src import MemoryService

# 初始化服务
service = MemoryService({
    "db_path": "~/.agent-memory/memory.db",
    "embedding": {
        "provider": "openai",
        "baseUrl": "http://localhost:8080/v1",
        "model": "bge-small-zh-v1.5",
        "dimensions": 512
    },
    "recall": {
        "maxResults": 5,
        "scoreThreshold": 0.3,
        "strategy": "hybrid"
    }
})

# 添加记忆
memory_id = service.add_memory(
    content="用户 Nick 对 AI Agent 框架非常感兴趣",
    keywords=["AI", "Agent", "OpenClaw"],
    session_id="sess_demo_001"
)
print(f"添加记忆: {memory_id}")

# 召回测试
results = service.recall("用户对什么技术感兴趣？")
print(f"召回结果:")
for r in results:
    print(f"  - [{r.get('score', 0):.2f}] {r['content'][:50]}...")

# 统计
stats = service.get_stats()
print(f"\n统计: {stats}")