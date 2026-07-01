"""
Memory Storage - 记忆存储层
SQLite + sqlite-vec 向量存储
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

class MemoryStorage:
    """记忆存储引擎"""

    def __init__(self, db_path: str = None):
        db_path = db_path or str(Path.home() / ".agent-memory" / "memory.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")

        # 记忆表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                keywords TEXT,
                metadata TEXT,
                session_id TEXT,
                layer TEXT DEFAULT 'L1',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 向量表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                memory_id TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)

        # 尝试创建向量索引（sqlite-vec）
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS vectors_ann
                USING vec0(embedding float[512])
            """)
        except:
            pass  # sqlite-vec 未安装，使用 fallback

        # 会话表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                messages TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 场景表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                keywords TEXT,
                memory_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 画像表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id TEXT PRIMARY KEY,
                name TEXT,
                traits TEXT,
                interests TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_memory(self, content: str, embedding: list[float],
                   keywords: list[str] = None, session_id: str = None,
                   metadata: dict = None, layer: str = "L1") -> str:
        """添加记忆"""
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO memories (id, content, keywords, metadata, session_id, layer) VALUES (?, ?, ?, ?, ?, ?)",
            (memory_id, content, json.dumps(keywords or []), json.dumps(metadata or {}), session_id, layer)
        )
        conn.execute(
            "INSERT INTO vectors (id, memory_id, embedding) VALUES (?, ?, ?)",
            (f"vec_{uuid.uuid4().hex[:12]}", memory_id, json.dumps(embedding))
        )
        conn.commit()
        conn.close()
        return memory_id

    def get_memory(self, memory_id: str) -> Optional[dict]:
        """获取单条记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM memories WHERE id = ?", (memory_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_similar(self, embedding: list[float], top_k: int = 5,
                       threshold: float = 0.3) -> list[dict]:
        """向量相似度搜索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("SELECT * FROM vectors")
        results = []

        for row in cursor.fetchall():
            stored_emb = json.loads(row["embedding"])
            # 计算相似度
            sim = self._cosine_sim(embedding, stored_emb)
            if sim >= threshold:
                memory = self.get_memory(row["memory_id"])
                if memory:
                    memory["similarity"] = sim
                    results.append(memory)

        conn.close()
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def search_keyword(self, keyword: str, top_k: int = 10) -> list[dict]:
        """关键词搜索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT * FROM memories WHERE content LIKE ? OR keywords LIKE ? ORDER BY created_at DESC",
            (f"%{keyword}%", f"%{keyword}%")
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results[:top_k]

    def add_session(self, session_id: str, messages: list[dict], metadata: dict = None):
        """添加会话"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO sessions (id, messages, metadata) VALUES (?, ?, ?)",
            (session_id, json.dumps(messages), json.dumps(metadata or {}))
        )
        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_stats(self) -> dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = lambda c: c.fetchone()[0]

        stats = {
            "memories": conn.execute("SELECT COUNT(*) FROM memories").fetchone(),
            "sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone(),
            "scenes": conn.execute("SELECT COUNT(*) FROM scenes").fetchone(),
            "personas": conn.execute("SELECT COUNT(*) FROM personas").fetchone(),
        }
        conn.close()
        return stats

    @staticmethod
    def _cosine_sim(vec1: list[float], vec2: list[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot / (norm1 * norm2 + 1e-9)