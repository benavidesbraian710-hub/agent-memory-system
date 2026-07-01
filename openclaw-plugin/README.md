# OpenClaw Plugin Mode

本目录包含用于 OpenClaw 的 memory-tdai 插件配置。

## 使用方式

1. 将 `config/memory-tencentdb.json` 复制到 `~/.openclaw/memory-tencentdb.json`

2. 配置 embedding 服务：
   - 本地模式：启动 `embedding_server.py`
   - 或使用其他 OpenAI 兼容 API

3. 重启 OpenClaw Gateway：
   ```bash
   launchctl stop ai.openclaw.gateway
   launchctl start ai.openclaw.gateway
   ```

## 配置说明

详见 `config/memory-tencentdb.json`，主要参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| capture.enabled | 启用对话捕获 | true |
| recall.strategy | 召回策略 | hybrid |
| embedding.provider | 向量服务 | openai |

## 前提条件

- OpenClaw Gateway 已安装
- embedding 服务运行在 `http://localhost:8080`（或修改 baseUrl）