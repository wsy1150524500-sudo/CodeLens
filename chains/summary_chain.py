"""文档总结链：对整篇文档生成摘要。"""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models.llm import get_llm

_SUMMARY_TEMPLATE = """你是一个专业的文档总结助手。请对以下文档内容进行全面、准确的总结。

要求：
1. 提炼文档的核心要点和关键信息
2. 保持总结结构清晰，使用分点列出
3. 总结长度控制在原文的 20%-30%

文档内容：
{text}

总结："""

_prompt = PromptTemplate(
    template=_SUMMARY_TEMPLATE,
    input_variables=["text"],
)


def build_summary_chain():
    """构建文档总结链。"""
    llm = get_llm(temperature=0.3)
    return _prompt | llm | StrOutputParser()


def summarize_text(text: str) -> str:
    """对文本执行总结。"""
    chain = build_summary_chain()
    return chain.invoke({"text": text})


async def stream_summarize(text: str):
    """流式文档总结，逐 token 产出。"""
    chain = build_summary_chain()
    async for chunk in chain.astream({"text": text}):
        yield chunk
