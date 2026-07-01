# Agent Memory System

AI Agent 记忆系统，参考 **TencentDB Agent Memory** 架构，包含完整的**官方源码**和**独立实现**两种版本。

## 项目结构

```
agent-memory-system/
├── memory-tencentdb-src/        # TencentDB 官方源码（95 个 TS 文件）
│   ├── src/core/                # 核心模块
│   ├── src/adapters/            # 适配器
│   ├── src/gateway/             # 网关
│   ├── src/offload/             # 上下文卸载
│   └── package.json
│
├── src/                         # 独立实现（Python，可用于任何框架）
│   ├── memory_service.py        # 统一接口
│   ├── embedding.py             # 向量化引擎
│   ├── storage.py               # SQLite 存储
│   └── recall.py                # RRF 召回算法
│
├── standalone-api/              # 独立 API 服务（Python）
│   ├── server.py
│   └── client.py
│
├── openclaw-plugin/             # OpenClaw 插件配置
│   └── config/memory-tencentdb.json
│
└── embedding_server.py          # 本地 BGE embedding 服务
```

## 核心能力

| 功能 | memory-tencentdb (TS) | agent-memory (Python) |
|------|----------------------|----------------------|
| L0 原始对话捕获 | ✅ | ✅ |
| L1 记忆提取 | ✅ 完整 LLM | ✅ 简化版 |
| L2 场景归纳 | ✅ | ✅ 框架 |
| L3 用户画像 | ✅ | ✅ 框架 |
| 向量搜索 | ✅ | ✅ |
| RRF 混合召回 | ✅ | ✅ |
| 存储 | SQLite + vec | SQLite |

## 两种使用方式

### 方式一：基于 TencentDB Agent Memory（推荐 OpenClaw 用户）

使用官方插件，在 OpenClaw 中直接启用：

```bash
# 复制配置
cp openclaw-plugin/config/memory-tencentdb.json ~/.openclaw/memory-tencentdb.json

# 重启 Gateway
launchctl stop ai.openclaw.gateway && launchctl start ai.openclaw.gateway
```

### 方式二：独立 Python 服务（适合任何框架）

```bash
cd standalone-api
pip install -r requirements.txt
python server.py
```

然后用 client 调用：
```python
from client import MemoryClient
client = MemoryClient()
client.add_memory("用户喜欢 AI", keywords=["AI"])
client.recall("用户兴趣是什么？")
```

## 启动 Embedding 服务（两种方式都需要）

```bash
python embedding_server.py
```

## 官方源码说明

`memory-tencentdb-src/` 目录包含 TencentDB Agent Memory 的完整 TypeScript 源码：
- 来自 `~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/`
- 95 个 TypeScript 文件
- 可作为开发参考或二次开发

如需作为 npm 包使用，参考其 `package.json` 的 `"scripts"` 和 `"dependencies"`。

## License

- 自实现部分: MIT
- TencentDB Agent Memory 源码: 见 `memory-tencentdb-src/LICENSE`