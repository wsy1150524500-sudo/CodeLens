# 阶段1：构建前端
FROM node:18-alpine AS frontend
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# 阶段2：运行后端
FROM python:3.11-slim
WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY main.py config.py expert_profile.yaml ./
COPY agent/ ./agent/
COPY api/ ./api/
COPY chains/ ./chains/
COPY document/ ./document/
COPY expert/ ./expert/
COPY knowledge_base/ ./knowledge_base/
COPY models/ ./models/
COPY vectorstore/ ./vectorstore/

# 复制前端构建产物
COPY --from=frontend /app/web/dist ./web/dist

# 创建运行时目录
RUN mkdir -p vectorstore/faiss_index uploads chat_history

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
