"""
Agent Memory System - Core Engine
通用记忆系统核心，可独立使用或作为 OpenClaw 插件
"""

from .memory_service import MemoryService
from .storage import MemoryStorage
from .embedding import EmbeddingEngine
from .recall import RecallEngine

__version__ = "1.0.0"
__all__ = ["MemoryService", "MemoryStorage", "EmbeddingEngine", "RecallEngine"]