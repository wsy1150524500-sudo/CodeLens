import os
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3.5-plus")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "qwen3-vl-embedding")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# FAISS 持久化路径
FAISS_INDEX_DIR: str = os.path.join(os.path.dirname(__file__), "vectorstore", "faiss_index")

# 上传文件临时目录
UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "uploads")

# 对话记忆窗口大小
MEMORY_WINDOW_K: int = 3

# 对话历史持久化目录
CHAT_HISTORY_DIR: str = os.path.join(os.path.dirname(__file__), "chat_history")

# Embedding 并发数（控制同时发出的 API 请求数）
EMBEDDING_CONCURRENCY: int = int(os.getenv("EMBEDDING_CONCURRENCY", "5"))
