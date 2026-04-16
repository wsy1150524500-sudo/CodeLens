"""RAG 问答链：检索相关文档 + LLM 生成带来源引用的回答。"""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models.llm import get_llm
from vectorstore.store import get_retriever

_RAG_TEMPLATE = """你是一个专业的文档问答助手。请根据以下参考文档回答用户问题。

要求：
1. 仅基于参考文档内容回答，不要编造信息
2. 在回答末尾标注引用来源（文件名和片段编号）
3. 如果文档中没有相关信息，请明确告知用户

参考文档：
{context}

用户问题：{question}

回答："""

_prompt = PromptTemplate(
    template=_RAG_TEMPLATE,
    input_variables=["context", "question"],
)


def _format_docs(docs) -> str:
    """将检索到的文档格式化为带来源标注的文本。"""
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "未知")
        idx = doc.metadata.get("chunk_index", "?")
        parts.append(f"[来源: {source} #片段{idx}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_rag_chain(k: int = 4):
    """构建 RAG 问答链。"""
    retriever = get_retriever(k=k)
    llm = get_llm(temperature=0.3)

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | _prompt
        | llm
        | StrOutputParser()
    )
    return chain


async def stream_rag_chain(query: str, k: int = 4):
    """流式 RAG 问答，逐 token 产出。"""
    chain = build_rag_chain(k=k)
    async for chunk in chain.astream(query):
        yield chunk
