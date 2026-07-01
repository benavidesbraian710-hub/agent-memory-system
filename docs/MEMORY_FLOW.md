# 记忆流转文档

## 1. 记忆生命周期

```
┌──────────────────────────────────────────────────────────────┐
│                     用户对话进行中                            │
│  User: "我想了解一下 OpenClaw"                               │
│  Assistant: "OpenClaw 是一个 AI Agent 框架..."              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L0 原始对话捕获                            │
│  capture.enabled = true 时，每次对话自动写入 sessions/       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L1 记忆提取触发                            │
│  触发条件:                                                    │
│    - everyNConversations = 5 时                              │
│    - 空闲 l1IdleTimeoutSeconds 后首次回复                     │
│    - Session 结束时                                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L1 记忆提取执行                            │
│  1. LLM 分析对话，提取关键信息                                │
│  2. 生成 keywords                                            │
│  3. 调用 embedding API 生成向量                              │
│  4. 存入 memories/ + vectors.db                             │
│  5. 去重检测（enableDedup = true 时）                        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L2 场景归纳触发                            │
│  触发条件:                                                    │
│    - L1 完成且距上次 L2 > l2MinIntervalSeconds               │
│    - 新记忆数达到 triggerEveryN（默认 50 条）                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L2 场景归纳执行                            │
│  1. 聚类分析所有 memories                                    │
│  2. 跨 session 归纳主题场景                                  │
│  3. 生成 scene.name, scene.description                       │
│  4. 存入 scenes/                                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L3 画像生成触发                            │
│  触发条件: 随 L2 一起生成                                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    L3 画像生成执行                            │
│  1. 综合分析所有 scenes                                      │
│  2. 提取用户特征、偏好、习惯                                  │
│  3. 生成 persona.traits, persona.interests                   │
│  4. 存入 personas/ + 备份旧版本                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                       记忆召回                                │
│  当用户问及相关问题时:                                        │
│  1. 接收用户查询                                             │
│  2. 生成查询向量                                             │
│  3. hybrid 召回（keyword + embedding）                        │
│  4. RRF 融合排序                                             │
│  5. 阈值过滤                                                 │
│  6. 返回 Top-N 记忆                                          │
└──────────────────────────────────────────────────────────────┘
```

## 2. 召回详细流程

### 2.1 用户发起查询

```
用户: "我之前问过你关于 OpenClaw 的什么问题？"
```

### 2.2 查询向量生成

```python
query_text = "用户问到 OpenClaw 的问题"
query_vector = embedding_model.encode(query_text)  # [0.xxx, -0.xxx, ...]
```

### 2.3 多路召回

**Keyword 召回**:
```sql
SELECT * FROM memories
WHERE content LIKE '%OpenClaw%'
ORDER BY relevance_score
LIMIT 20
```

**Embedding 召回**:
```sql
SELECT memory_id, distance
FROM vectors_ann
WHERE embedding = ?
ORDER BY distance
LIMIT 20
```

### 2.4 RRF 融合

```python
def rrf(results, k=60):
    scores = defaultdict(float)
    for result in results:
        for i, r in enumerate(result):
            scores[r.id] += 1 / (k + i + 1)
    return sorted(scores.items(), key=lambda x: -x[1])

# 融合两路结果
keyword_results = [...]  # Keyword 召回
vector_results = [...]   # Embedding 召回
fused = rrf([keyword_results, vector_results])
```

### 2.5 阈值过滤

```python
fused = [r for r in fused if r.score >= scoreThreshold]
return fused[:maxResults]  # 返回 Top-5
```

## 3. 数据清理流程

```
定时任务（每天 03:00）
        │
        ▼
┌───────────────────────────────────────┐
│  检查 l0l1RetentionDays              │
│  删除超过 90 天的 sessions/          │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  清理孤立的向量数据                   │
│  vectors.db 中无对应 memory 的向量    │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  压缩 vectors.db                     │
│  VACUUM 优化存储空间                  │
└───────────────────────────────────────┘
```

## 4. 热身模式（Warmup）

开启后，新 session 的 L1 触发间隔逐步增加：

```
Session 第 1 轮对话 → 触发 L1
Session 第 2 轮对话 → 触发 L1
Session 第 4 轮对话 → 触发 L1
Session 第 8 轮对话 → 触发 L1
...
Session 第 N 轮对话 → 触发 L1（达到 everyNConversations）
```

**目的**: 加速早期记忆提取，新 session 快速建立记忆

## 5. 去重流程

```python
def dedup(new_memory, existing_memories):
    new_vec = new_memory.embedding

    for existing in existing_memories:
        similarity = cosine_similarity(new_vec, existing.vec)

        if similarity > 0.9:  # 阈值可调
            # 认为重复，合并或丢弃
            return existing  # 返回已存在的相似记忆

    return None  # 无重复
```

## 6. 多 Agent 记忆隔离

```json
"capture": {
  "excludeAgents": ["bench-judge-*", "test-*"]
}
```

匹配 excludeAgents 的 Agent 对话不会被捕获，也不会参与召回。