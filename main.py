import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
from expert.knowledge_loader import load_knowledge_base
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="代码分析助手", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": app.version}


# 启动时确保必要目录存在
@app.on_event("startup")
async def startup():
    os.makedirs(config.FAISS_INDEX_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(config.CHAT_HISTORY_DIR, exist_ok=True)

    # 自动加载预置知识库
    logger.info("正在加载预置知识库...")
    result = await load_knowledge_base()
    if result["total_loaded"] > 0:
        for item in result["loaded"]:
            logger.info(f"  ✅ 已加载: {item['file']} ({item['chunks']} 片段)")
    if result["total_skipped"] > 0:
        for item in result["skipped"]:
            logger.info(f"  ⏭️  跳过: {item['file']} ({item['reason']})")
    logger.info(
        f"知识库加载完成: {result['total_loaded']} 新增, "
        f"{result['total_skipped']} 跳过"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Docker 部署时托管前端静态文件
_frontend_dir = os.path.join(os.path.dirname(__file__), "web", "dist")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
