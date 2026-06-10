# Dockerfile —— Mellow 单进程部署（前端 + 后端）
# 多阶段构建：先构建前端，再打包后端 + 前端静态文件

# ---- Stage 1: 构建前端 ----
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

# 安装依赖
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --prefer-offline

# 构建前端（VITE_API_BASE_URL 留空 = 相对路径 /api/v1，同源部署）
ENV VITE_API_BASE_URL=
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: 构建后端 + 前端静态文件 ----
FROM python:3.11-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# 后端源码
COPY backend/ ./

# 前端构建产物 → backend/static/
COPY --from=frontend-builder /build/frontend/dist ./static/

# 数据目录
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
