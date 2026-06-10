"""Mellow — 英语教学智能体 API 入口。"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from mellow.config import get_settings
from mellow.di import Container
from mellow.exceptions import MellowError, mellow_exception_handler

logger = logging.getLogger(__name__)

settings = get_settings()

# 前端静态文件目录（Vite 构建产物）
STATIC_DIR = Path(__file__).resolve().parent / "static"


async def _general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """捕获所有未被 MellowError 处理的异常，返回统一错误格式。"""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "服务器内部错误，请稍后重试。",
            "detail": {"exception": type(exc).__name__} if settings.debug else {},
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    # 初始化数据库
    from mellow.db import init_db
    container = Container.instance()
    engine = container._db_engine
    await init_db(engine)

    # 启动主动联系调度器
    from mellow.memory.scheduler import ProactiveScheduler
    scheduler = ProactiveScheduler(container)
    await scheduler.start()

    yield

    # 关闭
    await scheduler.stop()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name.title(),
    version=settings.app_version,
    description="角色扮演 + 自适应学习 + 即时语音互动的英语教学智能体。",
    lifespan=lifespan,
)

# CORS — 单进程部署后前后端同源，仅需允许 Capacitor WebView 跨域
# Capacitor WebView 的 origin 是 https://localhost，生产部署时与 API 不同源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 移动端 WebView origin 不固定，保持 *
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
# Starlette 按注册顺序匹配，子类必须排在父类前面。
# MellowError 是 Exception 的子类，先注册才能被正确捕获。
app.add_exception_handler(MellowError, mellow_exception_handler)
app.add_exception_handler(Exception, _general_exception_handler)

# ---- 注册路由 ----
from mellow.api.routes import auth, chat, persona, knowledge, profile, memory, voice, vocabulary, settings

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(persona.router)
app.include_router(knowledge.router)
app.include_router(profile.router)
app.include_router(memory.router)
app.include_router(voice.router)
app.include_router(vocabulary.router)
app.include_router(settings.router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# ---- 前端静态文件服务（单进程部署，前后端同源）----
#
# FastAPI 路由匹配规则（按匹配顺序）：
# 1. /docs, /redoc, /openapi.json — API 文档（FastAPI 自动注册）
# 2. /api/v1/* — 业务 API 路由（include_router 注册）
# 3. /health — 健康检查（显式路由）
# 4. /{path} — SPA fallback（catch-all，返回静态文件或 index.html）
#
# 当 backend/static/ 目录不存在时（纯后端模式），跳过 SPA 挂载，
# 服务仅提供 API，不影响现有功能。

if STATIC_DIR.is_dir():
    # SPA fallback：所有未匹配 API 路由的 GET 请求：
    #   - 若对应文件存在于 static/ → 返回该文件（JS/CSS/图片/favicon 等）
    #   - 否则 → 返回 index.html（让 React Router 处理 URL）
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        """SPA fallback — 返回静态文件或 index.html。"""
        candidate = STATIC_DIR / full_path
        if full_path and ".." not in full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html")

    logger.info("前端 SPA 已挂载（静态目录: %s）", STATIC_DIR)
else:
    logger.warning(
        "前端静态文件目录不存在: %s — 跳过 SPA 挂载。"
        "请运行 `build.sh` 将前端构建产物复制到 backend/static/。",
        STATIC_DIR,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
