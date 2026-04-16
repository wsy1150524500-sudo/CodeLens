"""文档注册表：追踪已入库文件，基于内容 hash 去重。"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Optional

import config

# 注册表文件路径（与 FAISS 索引同目录）
_REGISTRY_PATH = os.path.join(config.FAISS_INDEX_DIR, "doc_registry.json")


def _load_registry() -> Dict[str, str]:
    """加载注册表 {filename: content_hash}。"""
    if os.path.exists(_REGISTRY_PATH):
        with open(_REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_registry(registry: Dict[str, str]) -> None:
    """持久化注册表。"""
    os.makedirs(os.path.dirname(_REGISTRY_PATH), exist_ok=True)
    with open(_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def compute_hash(content: bytes) -> str:
    """计算文件内容的 SHA256 hash。"""
    return hashlib.sha256(content).hexdigest()


def is_duplicate(filename: str, content_hash: str) -> bool:
    """检查文件是否已入库（同名且内容相同）。"""
    registry = _load_registry()
    return registry.get(filename) == content_hash


def register_file(filename: str, content_hash: str) -> None:
    """将文件注册到已入库记录。"""
    registry = _load_registry()
    registry[filename] = content_hash
    _save_registry(registry)


def list_documents() -> List[Dict[str, str]]:
    """列出所有已入库的文档。"""
    registry = _load_registry()
    return [{"filename": k, "hash": v[:12]} for k, v in registry.items()]


def get_document_count() -> int:
    """获取已入库文档数量。"""
    return len(_load_registry())
