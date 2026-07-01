# Agent Memory System - 详细架构文档

## 1. 系统概述

Agent Memory System 是基于 OpenClaw Gateway 的四层记忆管理系统，为 AI Agent 提供持久化、层级化的记忆能力。

### 1.1 设计目标

- **记忆持久化**: 跨 session 保持记忆
- **自动提取**: 后台自动提取关键信息，无需人工干预
- **智能召回**: 混合搜索策略，精准匹配上下文
- **免费部署**: 完全本地运行，无 API 费用

### 1.2 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Gateway | OpenClaw | session 管理、路由、LLM 调用 |
| Memory | memory-tdai | 四层记忆系统 |
| 向量引擎 | BGE-small-zh-v1.5 | 512维中文 embedding |
| 存储 | SQLite + sqlite-vec | 本地向量数据库 |
| API 服务 | FastAPI | OpenAI 兼容接口 |

## 2. 四层记忆架构

### 2.1 L0 - 原始对话层

**职责**: 完整捕获每次对话的原文

**存储**: `~/.openclaw/memory-tencentdb/sessions/`

**特点**:
- 完整保留对话历史
- 支持回溯查询
- 可配置保留天数（默认 90 天）

**数据格式**:
```json
{
  "session_id": "abc123",
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好"}
  ],
  "timestamp": "2026-07-01T10:00:00Z"
}
```

### 2.2 L1 - 记忆提取层

**职责**: 从对话中自动提取关键记忆片段

**触发条件**:
- 每 5 轮对话
- 空闲 10 分钟后首次回复前
- Session 结束时

**存储**: `~/.openclaw/memory-tencentdb/memories/`

**特点**:
- 自动向量化存储
- 智能去重（基于向量相似度）
- 每 session 最多提取 10 条

**数据格式**:
```json
{
  "id": "mem_001",
  "content": "用户对 AI Agent 框架感兴趣，特别是 OpenClaw",
  "keywords": ["AI", "OpenClaw", "框架"],
  "embedding": [0.123, -0.456, ...],
  "session_id": "abc123",
  "created_at": "2026-07-01T10:05:00Z"
}
```

### 2.3 L2 - 场景归纳层

**职责**: 跨对话归纳主题场景

**触发条件**: 每 50 条新记忆触发 L2 批处理

**存储**: `~/.openclaw/memory-tencentdb/scenes/`

**特点**:
- 多会话关联分析
- 自动生成场景标签
- 最多保留 15 个活跃场景

**数据格式**:
```json
{
  "id": "scene_001",
  "name": "AI Agent 开发",
  "description": "用户关注各种 AI Agent 框架的对比和使用",
  "keywords": ["OpenClaw", "Agent", "记忆系统"],
  "memory_count": 23,
  "created_at": "2026-07-01T12:00:00Z"
}
```

### 2.4 L3 - 用户画像层

**职责**: 总结用户的偏好、习惯、关注领域

**触发条件**: 随 L2 一起生成

**存储**: `~/.openclaw/memory-tencentdb/personas/`

**特点**:
- 跨场景综合分析
- 生成用户特征标签
- 保留 3 个历史备份

**数据格式**:
```json
{
  "id": "persona_001",
  "name": "技术开发者 Nick",
  "traits": [
    "偏好开源技术",
    "关注 AI Agent 领域",
    "喜欢免费解决方案",
    "技术背景深厚"
  ],
  "interests": ["OpenClaw", "Hermes", "AI"],
  "updated_at": "2026-07-01T12:00:00Z"
}
```

## 3. 召回流程

### 3.1 召回策略

memory-tdai 支持三种召回策略：

1. **keyword**: 关键词精确匹配
2. **embedding**: 向量相似度搜索
3. **hybrid**: RRF 融合（推荐）

### 3.2 Hybrid 召回流程

```
用户查询
    │
    ▼
┌─────────────────┐
│  Keyword 搜索   │ ← BM25 / 全文索引
└────────┬────────┘
         │
         ▼ (RRF 融合)
┌─────────────────┐
│ Embedding 搜索  │ ← 向量相似度
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RRF 融合排序   │ ← Reciprocal Rank Fusion
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  阈值过滤       │ ← scoreThreshold = 0.3
└────────┬────────┘
         │
         ▼
    返回 Top-N 结果
```

### 3.3 RRF 算法

```python
def rrf_score(rank, k=60):
    """RRF 评分公式"""
    return 1 / (k + rank)

# 多路召回结果融合
combined_scores = {}
for result in keyword_results:
    combined_scores[result.id] += rrf_score(result.rank, k=60)
for result in vector_results:
    combined_scores[result.id] += rrf_score(result.rank, k=60)
```

## 4. 数据存储

### 4.1 目录结构

```
~/.openclaw/memory-tencentdb/
├── sessions/           # L0 原始对话
│   ├── 2026/
│   │   └── 07/
│   │       └── session_abc123.json
├── memories/           # L1 记忆片段
│   ├── memory_001.json
│   └── memory_002.json
├── scenes/             # L2 场景
│   └── scene_001.json
├── personas/           # L3 画像
│   ├── current.json
│   └── backup/
├── vectors.db          # 向量数据库 (sqlite-vec)
└── metadata.db         # 元数据
```

### 4.2 向量数据库

使用 sqlite-vec 实现向量存储：

```sql
CREATE TABLE vectors (
  id TEXT PRIMARY KEY,
  memory_id TEXT,
  embedding BLOB,
  created_at TIMESTAMP
);

CREATE VIRTUAL TABLE vectors_ann USING vec0(
  embedding float[512],
  memory_id TEXT
);
```

## 5. 配置参数

### 5.1 capture 配置

```json
"capture": {
  "enabled": true,              // 是否启用自动捕获
  "excludeAgents": [],          // 排除的 Agent glob 列表
  "l0l1RetentionDays": 90,      // L0/L1 保留天数
  "cleanTime": "03:00"          // 每日清理执行时间
}
```

### 5.2 extraction 配置

```json
"extraction": {
  "enabled": true,              // 是否启用 L1 提取
  "enableDedup": true,          // 是否启用去重
  "maxMemoriesPerSession": 10   // 每 session 最大记忆数
}
```

### 5.3 pipeline 配置

```json
"pipeline": {
  "everyNConversations": 5,     // 每 N 轮对话触发 L1
  "enableWarmup": true,         // 热身模式（加速早期记忆提取）
  "l1IdleTimeoutSeconds": 600,  // L1 空闲超时
  "l2DelayAfterL1Seconds": 10,  // L1 后延迟触发 L2
  "l2MinIntervalSeconds": 900,  // L2 最小间隔
  "l2MaxIntervalSeconds": 3600, // L2 最大间隔
  "sessionActiveWindowHours": 24 // session 活跃窗口
}
```

### 5.4 embedding 配置

```json
"embedding": {
  "enabled": true,              // 是否启用向量搜索
  "provider": "openai",         // 提供商（openai兼容）
  "baseUrl": "http://localhost:8080/v1",  // API 地址
  "apiKey": "no-key",           // API Key
  "model": "bge-small-zh-v1.5", // 模型名称
  "dimensions": 512,            // 向量维度
  "timeoutMs": 10000            // 超时时间
}
```

## 6. API 接口

### 6.1 Embedding 服务

**POST /v1/embeddings**

```bash
curl -X POST http://localhost:8080/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "要嵌入的文本"}'
```

响应:
```json
{
  "object": "list",
  "model": "BAAI/bge-small-zh-v1.5",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, ...],
      "index": 0
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## 7. 性能优化

### 7.1 启动速度优化

模型在服务启动时加载一次，之后复用：
```python
# 全局单例
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')  # 启动时加载
```

### 7.2 并发处理

FastAPI 自动处理并发请求，模型支持批处理：
```python
texts = req.input if isinstance(req.input, list) else [req.input]
embeddings = model.encode(texts)  # 批量编码
```

### 7.3 内存管理

- L0/L1 数据超过 90 天自动清理
- 凌晨 3 点执行清理任务
- 向量数据库定期压缩