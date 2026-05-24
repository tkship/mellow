"""依赖注入容器 —— 管理所有 Provider 和 Service 的生命周期。"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mellow.config import Settings, get_settings


class Container:
    """简易 IoC 容器。

    所有 Provider 和 Service 通过 _lazy() 惰性初始化。
    """

    _instance: "Container | None" = None

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._cache: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def settings(self) -> Settings:
        return self._settings

    async def _lazy(self, key: str, factory):
        """惰性初始化并缓存实例。

        使用 asyncio.Lock 保护临界区，防止并发初始化导致资源泄漏。
        """
        if key in self._cache:
            return self._cache[key]
        async with self._lock:
            if key in self._cache:
                return self._cache[key]
            result = factory()
            if asyncio.iscoroutine(result):
                result = await result
            self._cache[key] = result
            return result

    # ---- 数据库 ----
    @property
    def _db_engine(self):
        """惰性创建数据库引擎（同步属性，不缓存到 _cache）。"""
        from mellow.db.engine import get_engine

        if "_db_engine" not in self.__dict__:
            self.__dict__["_db_engine_val"] = get_engine(self._settings)
            self.__dict__["_db_engine"] = True
        return self.__dict__["_db_engine_val"]

    @property
    def _session_factory(self) -> async_sessionmaker[AsyncSession]:
        """惰性创建 session 工厂。"""
        from mellow.db.engine import get_session_factory

        if "_session_factory" not in self.__dict__:
            self.__dict__["_session_factory_val"] = get_session_factory(self._db_engine)
            self.__dict__["_session_factory"] = True
        return self.__dict__["_session_factory_val"]

    def session(self) -> AsyncSession:
        """创建一个新的 AsyncSession。"""
        return self._session_factory()

    def user_repo(self) -> "SqlAlchemyUserRepository":
        """创建 UserRepository 实例。"""
        from mellow.db.repos.user_repo import SqlAlchemyUserRepository

        return SqlAlchemyUserRepository(self.session())

    # ---- LLM ----
    async def llm(self):
        from mellow.llm.client import OpenAIProvider
        return await self._lazy("llm", lambda: OpenAIProvider(self._settings))

    async def llm_router(self):
        from mellow.llm.router import LLMRouter

        async def _factory():
            # 直接创建依赖以避免在持有锁时通过 _lazy 递归获取 llm
            from mellow.llm.client import OpenAIProvider
            llm = OpenAIProvider(self._settings)
            return LLMRouter(self._settings, llm)

        return await self._lazy("llm_router", _factory)

    # ---- Knowledge ----
    async def knowledge(self):
        from mellow.knowledge.implementations.open_english_dict import OpenEnglishDictProvider
        return await self._lazy("knowledge", lambda: OpenEnglishDictProvider())

    # ---- Embedding ----
    async def embedding(self):
        return await self._lazy("embedding", self._create_embedding)

    def _create_embedding(self):
        provider_name = self._settings.embed_provider
        if provider_name == "dashscope":
            from mellow.embedding.implementations.dashscope import DashScopeEmbeddingProvider
            return DashScopeEmbeddingProvider(self._settings)
        elif provider_name == "siliconflow":
            from mellow.embedding.implementations.siliconflow import SiliconFlowEmbeddingProvider
            return SiliconFlowEmbeddingProvider(self._settings)
        else:
            raise ValueError(f"不支持的 Embedding 提供商: {provider_name}")

    # ---- Vector Store ----
    async def vector_store(self):
        from mellow.vector_store.connection import LanceDBConnector
        connector = LanceDBConnector(self._settings)
        return await self._lazy("vector_store", lambda: connector)

    # ---- Auth ----
    async def auth(self):
        from mellow.auth.jwt_auth import JWTAuthProvider
        return await self._lazy("auth", lambda: JWTAuthProvider(self._settings, session_factory=self._session_factory))

    # ---- Agent ----
    async def agent(self):
        return await self._lazy("agent", self._create_agent)

    async def _create_agent(self):
        from mellow.agent.orchestrator import OrchestratorAgent
        from mellow.agent.chat_agent import ChatAgent
        from mellow.agent.teach_agent import TeachAgent
        from mellow.agent.reflect_agent import ReflectAgent
        from mellow.llm.router import LLMRouter
        from mellow.llm.client import OpenAIProvider

        # 直接创建依赖以避免在持有锁时通过 _lazy 递归获取
        llm = OpenAIProvider(self._settings)
        llm_router = LLMRouter(self._settings, llm)

        orchestrator = OrchestratorAgent(llm_router)
        orchestrator._set_agents(
            chat_agent=ChatAgent(llm),
            teach_agent=TeachAgent(llm),
            reflect_agent=ReflectAgent(llm),
        )
        return orchestrator

    # ---- Persona ----
    async def persona_manager(self):
        from mellow.persona.manager import PersonaManager
        return await self._lazy("persona_manager", lambda: PersonaManager(self._settings))

    # ---- Memory ----
    async def profile_manager(self):
        from mellow.db.repos.profile_repo import SqlAlchemyLearningProfileRepository
        from mellow.memory.learning_profile import LearningProfileManager
        repo = SqlAlchemyLearningProfileRepository(self.session())
        return await self._lazy("profile_manager", lambda: LearningProfileManager(repo))

    async def memory_manager(self):
        from mellow.db.repos.persona_memory_repo import SqlAlchemyPersonaMemoryRepository
        from mellow.memory.persona_memory import PersonaMemoryManager
        repo = SqlAlchemyPersonaMemoryRepository(self.session())
        return await self._lazy("memory_manager", lambda: PersonaMemoryManager(repo))

    # ---- Voice (Phase 8) ----
    # async def asr(self): ...
    # async def tts(self): ...

    # ---- Proactive Messenger ----
    async def proactive_messenger(self):
        from mellow.memory.proactive import ProactiveMessenger
        llm = await self.llm()
        return await self._lazy("proactive_messenger", lambda: ProactiveMessenger(llm))


async def get_container() -> AsyncGenerator[Container, None]:
    yield Container.instance()