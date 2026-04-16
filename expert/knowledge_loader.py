"""启动时自动加载预置知识库到向量库。"""

from __future__ import annotations

import os

from document.loader import load_file, split_documents
from vectorstore.store import async_add_documents
from vectorstore.registry import compute_hash, is_duplicate, register_file
from expert.profile import load_profile


async def load_knowledge_base() -> dict:
    """加载专家配置中指定的知识库文件到向量库。

    已入库的文件（内容未变）会自动跳过，支持增量更新。
    返回加载统计信息。
    """
    profile = load_profile()
    paths = profile.get_knowledge_paths()

    loaded = []
    skipped = []

    for path in paths:
        filename = os.path.basename(path)
        kb_filename = f"kb:{filename}"  # 加前缀区分知识库和用户文档

        if not os.path.exists(path):
            skipped.append({"file": filename, "reason": "文件不存在"})
            continue

        with open(path, "rb") as f:
            content_hash = compute_hash(f.read())

        if is_duplicate(kb_filename, content_hash):
            skipped.append({"file": filename, "reason": "已入库且未变化"})
            continue

        text = load_file(path)
        docs = split_documents(text, kb_filename)
        count = await async_add_documents(docs)
        register_file(kb_filename, content_hash)
        loaded.append({"file": filename, "chunks": count})

    return {
        "loaded": loaded,
        "skipped": skipped,
        "total_loaded": len(loaded),
        "total_skipped": len(skipped),
    }
