#!/usr/bin/env python3
"""
记忆统计脚本
查看当前记忆系统的数据统计
"""

import os
import json
from pathlib import Path
from datetime import datetime

MEMORY_BASE = Path.home() / ".openclaw" / "memory-tencentdb"

def count_files(directory: Path, pattern: str = "*.json") -> int:
    """统计目录下的文件数量"""
    if not directory.exists():
        return 0
    return len(list(directory.rglob(pattern)))

def get_memories_info() -> dict:
    """获取 memories 目录信息"""
    memories_dir = MEMORY_BASE / "memories"
    if not memories_dir.exists():
        return {"count": 0, "size": "0B"}

    files = list(memories_dir.rglob("*.json"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "count": len(files),
        "size": format_size(total_size)
    }

def get_sessions_info() -> dict:
    """获取 sessions 目录信息"""
    sessions_dir = MEMORY_BASE / "sessions"
    if not sessions_dir.exists():
        return {"count": 0, "size": "0B"}

    files = list(sessions_dir.rglob("*.json"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "count": len(files),
        "size": format_size(total_size)
    }

def get_scenes_info() -> dict:
    """获取 scenes 目录信息"""
    scenes_dir = MEMORY_BASE / "scenes"
    if not scenes_dir.exists():
        return {"count": 0}

    files = list(scenes_dir.rglob("*.json"))
    return {"count": len(files)}

def get_personas_info() -> dict:
    """获取 personas 目录信息"""
    personas_dir = MEMORY_BASE / "personas"
    if not personas_dir.exists():
        return {"count": 0}

    files = list(personas_dir.rglob("*.json"))
    return {"count": len(files)}

def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

def get_db_info() -> dict:
    """获取向量数据库信息"""
    vectors_db = MEMORY_BASE / "vectors.db"
    if not vectors_db.exists():
        return {"size": "0B"}

    size = vectors_db.stat().st_size
    return {"size": format_size(size)}

def main():
    print("=== Agent Memory System 统计 ===\n")
    print(f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据目录: {MEMORY_BASE}\n")

    print("┌─────────────────────────────────────┐")
    print("│           记忆层统计                 │")
    print("├───────────────┬─────────┬───────────┤")
    print("│     层级      │  数量   │    备注   │")
    print("├───────────────┼─────────┼───────────┤")

    # L0
    l0 = get_sessions_info()
    print(f"│ L0 原始对话   │ {l0['count']:>7} │ {l0['size']:>7} │")

    # L1
    l1 = get_memories_info()
    print(f"│ L1 记忆片段   │ {l1['count']:>7} │ {l1['size']:>7} │")

    # L2
    l2 = get_scenes_info()
    print(f"│ L2 场景       │ {l2['count']:>7} │           │")

    # L3
    l3 = get_personas_info()
    print(f"│ L3 用户画像   │ {l3['count']:>7} │           │")

    print("└───────────────┴─────────┴───────────┘")

    # 向量数据库
    db = get_db_info()
    print(f"\n向量数据库: {db['size']}")

    # 配置文件
    config = MEMORY_BASE.parent / "memory-tencentdb.json"
    if config.exists():
        with open(config) as f:
            cfg = json.load(f)
        print(f"\n配置状态:")
        print(f"  - 捕获: {'开启' if cfg.get('capture', {}).get('enabled') else '关闭'}")
        print(f"  - 召回: {'开启' if cfg.get('recall', {}).get('enabled') else '关闭'}")
        print(f"  - Embedding: {cfg.get('embedding', {}).get('provider', 'none')}")
        print(f"  - 召回策略: {cfg.get('recall', {}).get('strategy', 'N/A')}")

if __name__ == "__main__":
    main()