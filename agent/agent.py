"""Agent 核心：组装 LLM + Tools + Memory，根据用户意图自动路由。

对话历史通过 FileChatMessageHistory 持久化到本地文件，
每个 session_id 对应一个 JSON 文件，重启服务后记忆不丢失。
传入 Agent 时只取最近 K 轮作为上下文窗口。
"""

from __future__ import annotations

import os
from typing import AsyncIterator

from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from models.llm import get_llm
from agent.tools import get_all_tools
from expert.profile import load_profile
import config

_TOOL_INSTRUCTIONS = """

你可以使用以下工具：
- document_qa：当需要查阅知识库或用户上传的文档时使用
- document_summary：当用户要求总结文档内容时使用
对于不需要工具的问题，直接回答即可。"""


def _get_system_prompt() -> str:
    """从专家配置加载 system prompt。"""
    profile = load_profile()
    return profile.persona + _TOOL_INSTRUCTIONS


def _get_history(session_id: str) -> FileChatMessageHistory:
    """获取指定会话的持久化历史记录。"""
    file_path = os.path.join(config.CHAT_HISTORY_DIR, f"{session_id}.json")
    return FileChatMessageHistory(file_path=file_path)


def _get_recent_messages(history: FileChatMessageHistory, k: int) -> list:
    """从完整历史中取最近 k 轮对话作为上下文窗口。"""
    all_msgs = history.messages
    # 每轮 = 1 human + 1 ai = 2 条消息
    window = k * 2
    if len(all_msgs) <= window:
        return list(all_msgs)
    return list(all_msgs[-window:])


def _build_agent():
    """构建 ReAct Agent 实例。"""
    llm = get_llm(temperature=0.3)
    tools = get_all_tools()
    return create_react_agent(llm, tools, prompt=_get_system_prompt())


def run_agent(query: str, session_id: str = "default") -> str:
    """同步执行 Agent，返回完整回答。"""
    agent = _build_agent()
    history = _get_history(session_id)
    recent = _get_recent_messages(history, config.MEMORY_WINDOW_K)
    messages = recent + [HumanMessage(content=query)]

    result = agent.invoke({"messages": messages})

    # 提取最终回复
    answer = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            answer = msg.content
            break

    # 持久化到文件
    history.add_user_message(query)
    history.add_ai_message(answer)
    return answer


async def stream_agent(
    query: str, session_id: str = "default"
) -> AsyncIterator[str]:
    """流式执行 Agent，逐 token 产出文本。"""
    agent = _build_agent()
    history = _get_history(session_id)
    recent = _get_recent_messages(history, config.MEMORY_WINDOW_K)
    messages = recent + [HumanMessage(content=query)]

    full_answer = ""

    async for event in agent.astream_events(
        {"messages": messages}, version="v2"
    ):
        kind = event.get("event", "")
        if kind == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                if not getattr(chunk, "tool_calls", None) and not getattr(
                    chunk, "tool_call_chunks", None
                ):
                    full_answer += chunk.content
                    yield chunk.content

    # 流结束后持久化
    history.add_user_message(query)
    history.add_ai_message(full_answer)


def get_session_history(session_id: str) -> list:
    """获取指定会话的完整历史消息（供 API 返回给前端）。"""
    history = _get_history(session_id)
    messages = []
    for msg in history.messages:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    return messages


def list_sessions() -> list:
    """列出所有有历史记录的会话。"""
    import glob
    pattern = os.path.join(config.CHAT_HISTORY_DIR, "*.json")
    sessions = []
    for path in glob.glob(pattern):
        session_id = os.path.splitext(os.path.basename(path))[0]
        history = _get_history(session_id)
        msgs = history.messages
        # 用第一条用户消息作为标题
        title = session_id
        for msg in msgs:
            if isinstance(msg, HumanMessage):
                title = msg.content[:30] + ("..." if len(msg.content) > 30 else "")
                break
        sessions.append({"id": session_id, "title": title})
    return sessions


def delete_session(session_id: str) -> bool:
    """删除指定会话的历史记录文件。"""
    file_path = os.path.join(config.CHAT_HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
