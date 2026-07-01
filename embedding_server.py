#!/usr/bin/env python3
"""
本地 Embedding API 服务
使用 BGE-small-zh-v1.5 模型，512维
OpenAI 兼容接口格式

启动方式:
    python embedding_server.py

API 端点:
    POST /v1/embeddings
    Body: {"input": "要嵌入的文本"} 或 {"input": ["文本1", "文本2"]}

示例:
    curl -X POST http://localhost:8080/v1/embeddings \
      -H "Content-Type: application/json" \
      -d '{"input": "测试文本"}'
"""

from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="Local Embedding Service")

# 加载模型（启动时加载一次）
MODEL_NAME = os.environ.get("MODEL_NAME", "BAAI/bge-small-zh-v1.5")
model = SentenceTransformer(MODEL_NAME)

class EmbedRequest(BaseModel):
    input: str | list[str]
    model: str | None = None

class EmbedResponse(BaseModel):
    object: str = "list"
    model: str
    data: list
    usage: dict

@app.post("/v1/embeddings")
def embeddings(req: EmbedRequest):
    """生成文本 embedding"""
    texts = req.input if isinstance(req.input, list) else [req.input]
    embeddings = model.encode(texts).tolist()

    return {
        "object": "list",
        "model": MODEL_NAME,
        "data": [
            {"object": "embedding", "embedding": emb, "index": i}
            for i, emb in enumerate(embeddings)
        ],
        "usage": {
            "prompt_tokens": sum(len(t) for t in texts),
            "total_tokens": sum(len(t) for t in texts)
        }
    }

@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok", "model": MODEL_NAME}

@app.get("/")
def root():
    """根路径"""
    return {
        "service": "Local Embedding Service",
        "model": MODEL_NAME,
        "endpoints": {
            "embeddings": "POST /v1/embeddings",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"启动本地 Embedding 服务: http://localhost:{port}")
    print(f"模型: {MODEL_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=port)