"""Agent 工具定义：文档问答 Tool、文档总结 Tool。"""

from __future__ import annotations

from langchain_core.tools import tool

from chains.rag_chain import build_rag_chain
from chains.summary_chain import summarize_text
from vectorstore.store import has_index


@tool
def document_qa(query: str) -> str:
    """基于已上传的文档进行知识问答。当用户提出与文档内容相关的问题时使用此工具。
    输入应该是用户的具体问题。"""
    if not has_index():
        return "向量库为空，请先上传文档后再提问。"
    chain = build_rag_chain()
    return chain.invoke(query)


@tool
def document_summary(text: str) -> str:
    """对给定的文本内容进行总结摘要。当用户要求总结、概括文档内容时使用此工具。
    输入应该是需要总结的文本内容。"""
    return summarize_text(text)


def get_all_tools() -> list:
    """返回所有可用的 Agent 工具列表。"""
    return [document_qa, document_summary]
