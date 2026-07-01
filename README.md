# Agent Memory System

AI Agent 记忆系统，参考 **TencentDB Agent Memory** 的四层记忆架构，独立实现的版本。

## 核心能力

- **四层记忆架构**: L0 → L1 → L2 → L3 自动流转
- **向量搜索**: 本地 BGE-small-zh embedding，永久免费
- **混合召回**: keyword + vector RRF 融合，精准匹配
- **双模式支持**: OpenClaw 插件 / 独立 API 服务
- **完整中文文档**: 架构、配置、流程全覆盖

## 项目结构

```
agent-memory-system/
├── src/                         # 核心引擎（Python 独立实现）
│   ├── memory_service.py        # 统一服务接口
│   ├── embedding.py             # 向量化引擎
│   ├── storage.py               # SQLite 存储
│   ├── recall.py                # RRF 召回算法
│   └── extraction.py            # L1/L2/L3 提取
│
├── standalone-api/              # 独立 API 服务
│   ├── server.py                # FastAPI 服务
│   ├── client.py                # 调用示例
│   └── requirements.txt
│
├── openclaw-plugin/             # OpenClaw 插件配置
│   └── config/memory-tencentdb.json
│
├── embedding_server.py          # 本地 BGE embedding 服务
├── config/                      # 配置示例
└── docs/                        # 详细文档
    ├── ARCHITECTURE.md          # 架构设计
    ├── CONFIG.md                # 配置参数
    └── MEMORY_FLOW.md           # 记忆流转
```

## 快速开始

### 方式一：OpenClaw 插件

```bash
cp openclaw-plugin/config/memory-tencentdb.json ~/.openclaw/memory-tencentdb.json
python embedding_server.py  # 启动 embedding 服务
launchctl stop ai.openclaw.gateway && launchctl start ai.openclaw.gateway
```

### 方式二：独立 API（任何框架都能用）

```bash
cd standalone-api
pip install -r requirements.txt
python server.py  # 启动服务 http://localhost:18790
```

调用示例：
```python
from client import MemoryClient
client = MemoryClient()
client.add_memory("用户喜欢 AI 技术", keywords=["AI"])
results = client.recall("用户兴趣是什么？")
```

## 参考架构

本项目参考 TencentDB Agent Memory 的设计：
- 官方仓库: https://github.com/tencentdb/memory-tencentdb
- MIT License

## License

MIT