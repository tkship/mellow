"""Mellow — 英语教学智能体 API 入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mellow.config import get_settings
from mellow.di import Container
from mellow.exceptions import MellowError, mellow_exception_handler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    # 启动主动联系调度器
    from mellow.memory.scheduler import ProactiveScheduler
    container = Container.instance()
    scheduler = ProactiveScheduler(container)
    await scheduler.start()

    yield

    # 关闭
    await scheduler.stop()


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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
app.add_exception_handler(MellowError, mellow_exception_handler)

# ---- 注册路由 ----
from mellow.api.routes import auth, chat, persona, knowledge, profile, memory, voice

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(persona.router)
app.include_router(knowledge.router)
app.include_router(profile.router)
app.include_router(memory.router)
app.include_router(voice.router)


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
