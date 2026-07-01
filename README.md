# Agent Memory System

基于 OpenClaw 的四层记忆系统，为 AI Agent 提供持久化记忆能力。

## 核心特性

- **四层记忆架构**: L0 原始对话 → L1 记忆提取 → L2 场景归纳 → L3 用户画像
- **向量搜索**: 本地 BGE-small-zh embedding，512维，永久免费
- **混合召回**: keyword + vector RRF 融合，召回精准
- **自动提取**: 后台异步处理，不影响对话流畅度
- **去重检测**: 基于向量相似度智能去重，避免记忆冗余

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                         │
│              (session 管理 + 路由 + LLM 调用)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               memory-tdai (四层记忆系统)                     │
│                                                             │
│  L0 原始对话   →  捕获每次对话原文                            │
│      ↓                                                   │
│  L1 记忆提取   →  自动提取关键信息（embedding 向量化）         │
│      ↓                                                   │
│  L2 场景归纳   →  跨对话归纳主题场景                          │
│      ↓                                                   │
│  L3 用户画像   →  总结用户的偏好/习惯/关注领域                │
│                                                             │
│  召回时：hybrid 策略（keyword + vector 混合）                 │
│  向量引擎：本地 BGE-small-zh（512维）                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLite 本地存储                             │
│   ~/.openclaw/memory-tencentdb/                             │
│   - sessions/      对话记录                                  │
│   - memories/      L1 记忆片段                               │
│   - scenes/        L2 场景                                   │
│   - personas/      L3 画像                                   │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
# 创建 conda 环境
conda create -n agent-memory python=3.11 -y
conda activate agent-memory

# 安装 sentence-transformers 和 fastapi
pip install sentence-transformers fastapi uvicorn
```

### 2. 配置 Embedding 服务

启动本地 embedding 服务：

```bash
python embedding_server.py
```

服务运行在 `http://localhost:8080/v1`，使用 BGE-small-zh-v1.5 模型。

### 3. 配置 memory-tdai

在 `~/.openclaw/memory-tencentdb.json` 中配置：

```json
{
  "capture": {
    "enabled": true,
    "excludeAgents": [],
    "l0l1RetentionDays": 90,
    "cleanTime": "03:00"
  },
  "extraction": {
    "enabled": true,
    "enableDedup": true,
    "maxMemoriesPerSession": 10
  },
  "pipeline": {
    "everyNConversations": 5,
    "enableWarmup": true,
    "l1IdleTimeoutSeconds": 600,
    "l2DelayAfterL1Seconds": 10,
    "l2MinIntervalSeconds": 900,
    "l2MaxIntervalSeconds": 3600,
    "sessionActiveWindowHours": 24
  },
  "recall": {
    "enabled": true,
    "maxResults": 5,
    "scoreThreshold": 0.3,
    "strategy": "hybrid"
  },
  "persona": {
    "triggerEveryN": 50,
    "maxScenes": 15,
    "backupCount": 3,
    "sceneBackupCount": 10
  },
  "embedding": {
    "enabled": true,
    "provider": "openai",
    "baseUrl": "http://localhost:8080/v1",
    "apiKey": "no-key",
    "model": "bge-small-zh-v1.5",
    "dimensions": 512
  }
}
```

### 4. 重启 Gateway

```bash
launchctl stop ai.openclaw.gateway
launchctl start ai.openclaw.gateway
```

## 项目结构

```
agent-memory-system/
├── README.md                 # 项目说明
├── LICENSE                   # MIT License
├── embedding_server.py       # 本地 embedding API 服务
├── config/
│   └── memory-tencentdb.json # memory-tdai 完整配置
├── scripts/
│   └── setup_embedding.sh    # 一键安装脚本
├── docs/
│   ├── ARCHITECTURE.md       # 详细架构文档
│   ├── API.md                # API 接口文档
│   ├── CONFIG.md             # 配置参数说明
│   └── MEMORY_FLOW.md        # 记忆流转文档
└── examples/
    ├── recall_example.py     # 召回示例
    └── memory_stats.py       # 记忆统计脚本
```

## 配置参数详解

### embedding 配置

| 参数 | 说明 | 值 |
|------|------|-----|
| provider | API 类型 | `openai` (兼容模式) |
| baseUrl | Embedding 服务地址 | `http://localhost:8080/v1` |
| model | 模型名称 | `bge-small-zh-v1.5` |
| dimensions | 向量维度 | `512` |
| apiKey | API Key | `no-key` (本地服务无需) |

### recall 配置

| 参数 | 说明 | 值 |
|------|------|-----|
| enabled | 是否启用召回 | `true` |
| maxResults | 最大召回条数 | `5` |
| scoreThreshold | 最低相似度阈值 | `0.3` |
| strategy | 召回策略 | `hybrid` (keyword + vector) |

### pipeline 配置

| 参数 | 说明 | 值 |
|------|------|-----|
| everyNConversations | 每 N 轮对话触发 L1 | `5` |
| enableWarmup | 热身模式 | `true` |
| l1IdleTimeoutSeconds | L1 空闲超时 | `600` |
| l2DelayAfterL1Seconds | L1 后延迟触发 L2 | `10` |
| l2MinIntervalSeconds | L2 最小间隔 | `900` |

## 适用场景

- **个人 AI 助手**: 跨 session 记忆用户偏好
- **Agent 开发**: 为 AI Agent 添加持久化记忆
- **多 Agent 系统**: 共享记忆层
- **客服机器人**: 记住用户历史交互

## 替代方案对比

| 方案 | 向量搜索 | 免费 | 部署难度 |
|------|---------|------|---------|
| memory-tdai + 本地 BGE | ✅ | ✅ | 中 |
| memory-tdai + SiliconFlow | ✅ | 部分免费 | 低 |
| OpenViking | ✅ | ✅ | 中 |
| OpenClaw 原生 | ❌ | ✅ | 低 |
| Tavily | ✅ | 部分免费 | 低 |

## License

MIT