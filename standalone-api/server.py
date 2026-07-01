#!/usr/bin/env python3
"""
Standalone Memory API Server
独立记忆服务，通过 HTTP API 供外部 Agent 调用

启动: python server.py
API 文档: http://localhost:18790/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

import sys
sys.path.insert(0, "..")

from src import MemoryService

app = FastAPI(title="Agent Memory System API", version="1.0.0")

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

# ============ 请求模型 ============

class AddMemoryRequest(BaseModel):
    content: str
    keywords: list[str] = []
    session_id: str = None
    metadata: dict = {}
    layer: str = "L1"

class RecallRequest(BaseModel):
    query: str
    strategy: str = "hybrid"
    top_k: int = None

class AddSessionRequest(BaseModel):
    session_id: str
    messages: list[dict]
    metadata: dict = {}

# ============ API 端点 ============

@app.post("/memory")
def add_memory(req: AddMemoryRequest):
    """添加记忆"""
    memory_id = service.add_memory(
        content=req.content,
        keywords=req.keywords,
        session_id=req.session_id,
        metadata=req.metadata,
        layer=req.layer
    )
    return {"memory_id": memory_id, "status": "added"}

@app.post("/recall")
def recall(req: RecallRequest):
    """召回记忆"""
    results = service.recall(
        query=req.query,
        strategy=req.strategy,
        top_k=req.top_k
    )
    return {"results": results, "count": len(results)}

@app.post("/session")
def add_session(req: AddSessionRequest):
    """添加会话"""
    service.add_session(
        session_id=req.session_id,
        messages=req.messages,
        metadata=req.metadata
    )
    return {"session_id": req.session_id, "status": "added"}

@app.get("/session/{session_id}")
def get_session(session_id: str):
    """获取会话"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.get("/stats")
def get_stats():
    """获取统计信息"""
    return service.get_stats()

@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    print("启动 Agent Memory API 服务: http://localhost:18790")
    uvicorn.run(app, host="0.0.0.0", port=18790)