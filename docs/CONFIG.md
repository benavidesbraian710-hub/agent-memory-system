# 配置参数详解

## 完整配置示例

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
    "dimensions": 512,
    "timeoutMs": 10000
  }
}
```

## capture 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | true | 是否启用自动对话捕获 |
| excludeAgents | string[] | [] | 排除的 Agent glob 模式列表，匹配的 agent 不会被捕获 |
| l0l1RetentionDays | number | 90 | L0/L1 本地文件保留天数，0=不清理 |
| cleanTime | string | "03:00" | 每日清理执行时间（HH:mm） |

**excludeAgents 示例**:
```json
"excludeAgents": ["bench-judge-*", "test-*"]
```

## extraction 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | true | 是否启用后台 L1 提取 |
| enableDedup | boolean | true | L1 智能去重（基于向量相似度） |
| maxMemoriesPerSession | number | 10 | 单次 L1 提取每 session 最大记忆条数 |

## pipeline 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| everyNConversations | number | 5 | 每 N 轮对话触发 L1 批处理 |
| enableWarmup | boolean | true | 热身模式：新 session 从 1 轮触发开始，每次 L1 后翻倍（1→2→4→...→everyN） |
| l1IdleTimeoutSeconds | number | 600 | L1 空闲超时（秒）：用户停止对话后多久触发 L1 批处理 |
| l2DelayAfterL1Seconds | number | 10 | L1 完成后延迟多久触发 L2（秒） |
| l2MinIntervalSeconds | number | 900 | 同一 session 两次 L2 抽取的最小间隔（秒） |
| l2MaxIntervalSeconds | number | 3600 | 同一活跃 session 的 L2 最大轮询间隔（秒） |
| sessionActiveWindowHours | number | 24 | session 活跃窗口（小时），超过此时间不活跃的 session 停止 L2 轮询 |

## recall 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | true | 是否启用自动召回 |
| maxResults | number | 5 | 召回最大结果数 |
| scoreThreshold | number | 0.3 | 最低分数阈值，低于此值的 结果被过滤 |
| strategy | string | "hybrid" | 搜索策略：`keyword`、`embedding`、`hybrid` |
| timeoutMs | number | 5000 | 召回整体超时（毫秒），超时后跳过记忆注入 |

**strategy 选项**:

| 值 | 说明 |
|----|------|
| keyword | 关键词匹配（BM25） |
| embedding | 向量相似度搜索 |
| hybrid | 混合 RRF 融合（推荐） |

## persona 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| triggerEveryN | number | 50 | 每 N 条新记忆触发画像生成 |
| maxScenes | number | 15 | 最大场景数 |
| backupCount | number | 3 | 画像备份保留数量 |
| sceneBackupCount | number | 10 | 场景块备份保留数量 |

## embedding 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | true | 是否启用向量搜索（若 provider=none 则实际被禁用） |
| provider | string | "none" | Embedding 服务提供者：`openai`、`azure`、`cohere` 等 |
| baseUrl | string | - | API Base URL（必填） |
| apiKey | string | - | API Key |
| model | string | - | 模型名称（必填） |
| dimensions | number | - | 向量维度（必填，需与所选模型匹配） |
| timeoutMs | number | 10000 | 单次 embedding API 调用超时（毫秒） |

**BGE-small-zh-v1.5 参数**:
```json
"embedding": {
  "provider": "openai",
  "baseUrl": "http://localhost:8080/v1",
  "apiKey": "no-key",
  "model": "bge-small-zh-v1.5",
  "dimensions": 512
}
```

## llm 配置（可选）

独立 LLM 配置，开启后 L1/L2/L3 提取使用指定的 API：

```json
"llm": {
  "enabled": false,
  "baseUrl": "https://api.openai.com/v1",
  "apiKey": "your-api-key",
  "model": "gpt-4o",
  "maxTokens": 4096,
  "timeoutMs": 120000
}
```

## offload 配置（可选）

多层上下文压缩系统：

```json
"offload": {
  "enabled": false,
  "mildOffloadRatio": 0.5,
  "aggressiveCompressRatio": 0.85
}
```

## 环境变量

| 变量 | 说明 |
|------|------|
| OPENCLAW_MEMORY_BACKEND | 存储后端：`sqlite` 或 `tcvdb` |
| TCVDB_URL | 腾讯云向量数据库 URL（仅 tcvdb 后端） |
| TCVDB_API_KEY | 腾讯云向量数据库 API Key |