"""Embedding 封装：同步 + 异步并发，通过 dashscope SDK 调用百炼多模态模型。"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

import dashscope
from dashscope import MultiModalEmbedding, MultiModalEmbeddingItemText
from langchain_core.embeddings import Embeddings

import config

# 线程池供异步方法复用（dashscope SDK 是同步的，需要包装）
_executor = ThreadPoolExecutor(max_workers=config.EMBEDDING_CONCURRENCY)


class DashScopeEmbedding(Embeddings):
    """通过 dashscope SDK 调用百炼 Embedding 模型。

    同步方法：embed_documents / embed_query（逐条串行）
    异步方法：aembed_documents / aembed_query（并发，受 EMBEDDING_CONCURRENCY 控制）
    """

    model: str = config.EMBEDDING_MODEL
    dimension: int = 1024

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dashscope.api_key = config.DASHSCOPE_API_KEY

    # ── 单条同步调用（内部基础方法）─────────────────────

    def _embed_one(self, text: str) -> List[float]:
        """同步调用一次 Embedding API。"""
        resp = MultiModalEmbedding.call(
            model=self.model,
            input=[MultiModalEmbeddingItemText(text=text, factor=1)],
            dimension=self.dimension,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Embedding 调用失败: {resp.code} - {resp.message}"
            )
        return resp.output["embeddings"][0]["embedding"]

    # ── 同步接口（LangChain 基类要求）─────────────────

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """同步串行：对文档列表生成 embedding。"""
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """同步：对单条查询生成 embedding。"""
        return self._embed_one(text)

    # ── 异步并发接口 ─────────────────────────────────

    async def _aembed_one(
        self, text: str, semaphore: asyncio.Semaphore
    ) -> List[float]:
        """异步包装：在线程池中执行同步调用，受信号量控制并发。"""
        async with semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(_executor, self._embed_one, text)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """异步并发：对文档列表并行生成 embedding。

        并发数受 config.EMBEDDING_CONCURRENCY 控制，避免打爆 API 限流。
        """
        sem = asyncio.Semaphore(config.EMBEDDING_CONCURRENCY)
        tasks = [self._aembed_one(t, sem) for t in texts]
        return await asyncio.gather(*tasks)

    async def aembed_query(self, text: str) -> List[float]:
        """异步：对单条查询生成 embedding。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._embed_one, text)
