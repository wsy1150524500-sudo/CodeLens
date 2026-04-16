from langchain_openai import ChatOpenAI
import config


def get_llm(temperature: float = 0.7, **kwargs) -> ChatOpenAI:
    """获取百炼 qwen LLM 实例（OpenAI 兼容接口）"""
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.LLM_BASE_URL,
        temperature=temperature,
        **kwargs,
    )
