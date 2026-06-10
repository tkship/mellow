#!/usr/bin/env bash
# Mellow 一键构建脚本 — 前后端单进程部署
#
# 用法:
#   ./build.sh          # 构建前端 + 将产物复制到 backend/static/
#   ./build.sh --docker # 以上步骤 + Docker 镜像构建
#
# 构建完成后：
#   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
#   → 同时服务前端页面和 API

set -euo pipefail

echo "====================================="
echo "  Mellow 单进程构建脚本"
echo "====================================="

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
STATIC_DIR="$BACKEND_DIR/static"

# ---- Step 1: 构建前端 ----
echo ""
echo "[1/3] 构建前端..."
cd "$FRONTEND_DIR"

# 安装依赖（如需要）
if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖..."
    npm install
fi

# 构建（.env.production 留空 = 使用相对路径 /api/v1）
echo "  执行 npm run build..."
npm run build

# ---- Step 2: 复制到 backend/static/ ----
echo ""
echo "[2/3] 复制前端构建产物到 backend/static/..."

# 清理旧的 static 目录
rm -rf "$STATIC_DIR"
mkdir -p "$STATIC_DIR"

# 复制所有构建产物
cp -r "$FRONTEND_DIR/dist/"* "$STATIC_DIR/"

echo "  复制完成: $(ls "$STATIC_DIR" | head -5) ..."

# ---- Step 3: 验证 ----
echo ""
echo "[3/3] 验证..."
if [ -f "$STATIC_DIR/index.html" ]; then
    echo "  ✓ index.html 存在"
else
    echo "  ✗ index.html 不存在！构建可能失败。"
    exit 1
fi

if [ -d "$STATIC_DIR/assets" ]; then
    echo "  ✓ assets/ 目录存在"
else
    echo "  ✗ assets/ 目录不存在！构建可能失败。"
    exit 1
fi

echo ""
echo "====================================="
echo "  ✓ 构建完成！"
echo ""
echo "  启动服务:"
echo "    cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "  访问 http://localhost:8000 即可同时获取前端页面和 API。"
echo "====================================="

# ---- 可选: Docker 构建 ----
if [ "${1:-}" = "--docker" ]; then
    echo ""
    echo "[额外] 构建 Docker 镜像..."
    cd "$PROJECT_ROOT"
    docker build -t mellow:latest .
    echo "  ✓ Docker 镜像构建完成: mellow:latest"
fi