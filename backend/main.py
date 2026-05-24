"""Mellow — 英语教学智能体 API 入口。"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mellow.config import get_settings
from mellow.di import Container
from mellow.exceptions import MellowError, mellow_exception_handler

logger = logging.getLogger(__name__)

settings = get_settings()


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
from mellow.api.routes import auth, chat, persona, knowledge, profile, memory, voice, vocabulary

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(persona.router)
app.include_router(knowledge.router)
app.include_router(profile.router)
app.include_router(memory.router)
app.include_router(voice.router)
app.include_router(vocabulary.router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
