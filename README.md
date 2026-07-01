# Agent Memory System

通用 AI Agent 记忆系统，支持**两种运行模式**，开箱即用。

## 核心特性

- **四层记忆架构**: L0 → L1 → L2 → L3 自动流转
- **向量搜索**: 本地 BGE-small-zh embedding，永久免费
- **混合召回**: keyword + vector RRF 融合，精准匹配
- **双模式支持**: OpenClaw 插件模式 / 独立 API 服务

## 两种运行模式

```
┌─────────────────────────────────────────────────────────────┐
│                    模式一: OpenClaw 插件                     │
│         适用于 OpenClaw 平台内的 Agent                       │
│         配置简单，一行启动                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    模式二: 独立 API 服务                      │
│         适用于任何框架开发的 Agent                            │
│         HTTP API 调用，跨平台                                 │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
agent-memory-system/
├── src/                          # 核心引擎（通用）
│   ├── memory_service.py         # 统一服务接口
│   ├── embedding.py              # 向量化引擎
│   ├── storage.py                # SQLite 存储
│   └── recall.py                 # RRF 召回算法
│
├── standalone-api/               # 模式二: 独立服务
│   ├── server.py                 # API 服务
│   ├── client.py                 # 调用示例
│   └── requirements.txt
│
├── openclaw-plugin/              # 模式一: OpenClaw 插件
│   ├── config/
│   │   └── memory-tencentdb.json # 插件配置
│   └── README.md
│
├── embedding_server.py           # Embedding 服务（BGE）
├── config/                       # 通用配置示例
├── docs/                         # 详细文档
│   ├── ARCHITECTURE.md
│   ├── CONFIG.md
│   └── MEMORY_FLOW.md
└── examples/                     # 使用示例
```

## 快速开始

### 模式一：OpenClaw 插件

```bash
# 1. 复制配置
cp openclaw-plugin/config/memory-tencentdb.json ~/.openclaw/memory-tencentdb.json

# 2. 启动 embedding 服务
python embedding_server.py

# 3. 重启 Gateway
launchctl stop ai.openclaw.gateway
launchctl start ai.openclaw.gateway
```

### 模式二：独立 API 服务

```bash
# 1. 安装依赖
cd standalone-api
pip install -r requirements.txt

# 2. 启动服务
python server.py

# 3. 客户端调用
from client import MemoryClient
client = MemoryClient()
client.add_memory("用户喜欢 AI 技术", keywords=["AI"])
results = client.recall("用户兴趣是什么？")
```

## 核心 API

### MemoryService (直接调用)

```python
from src import MemoryService

service = MemoryService(config)
service.add_memory("内容", keywords=["标签"])
results = service.recall("查询")
```

### HTTP API (远程调用)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/memory` | POST | 添加记忆 |
| `/recall` | POST | 召回记忆 |
| `/session` | POST | 添加会话 |
| `/stats` | GET | 获取统计 |

## 四层记忆架构

| 层级 | 名称 | 说明 |
|------|------|------|
| L0 | 原始对话 | 完整捕获对话原文 |
| L1 | 记忆提取 | 自动提取关键信息 + 向量化 |
| L2 | 场景归纳 | 跨对话归纳主题 |
| L3 | 用户画像 | 总结用户偏好特征 |

## 配置参数

详见 [docs/CONFIG.md](docs/CONFIG.md)

主要配置：
- `embedding.provider`: `openai` | `local`
- `embedding.baseUrl`: API 地址
- `recall.strategy`: `keyword` | `embedding` | `hybrid`
- `recall.maxResults`: 召回数量

## License

MIT