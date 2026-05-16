"""依赖注入容器 —— 管理所有 Provider 和 Service 的生命周期。"""

from collections.abc import AsyncGenerator
from typing import Any

from mellow.config import Settings, get_settings


class Container:
    """简易 IoC 容器。

    所有 Provider 和 Service 通过 _lazy() 惰性初始化。
    """

    _instance: "Container | None" = None

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._cache: dict[str, Any] = {}

    @classmethod
    def instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def settings(self) -> Settings:
        return self._settings

    def _lazy(self, key: str, factory):
        """惰性初始化并缓存实例。"""
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]

    # ---- LLM ----
    @property
    def llm(self):
        from mellow.llm.client import OpenAIProvider
        return self._lazy("llm", lambda: OpenAIProvider(self._settings))

    @property
    def llm_router(self):
        from mellow.llm.router import LLMRouter
        return self._lazy("llm_router", lambda: LLMRouter(self._settings, self.llm))

    # ---- Knowledge ----
    @property
    def knowledge(self):
        from mellow.knowledge.implementations.open_english_dict import OpenEnglishDictProvider
        return self._lazy("knowledge", lambda: OpenEnglishDictProvider())

    # ---- Embedding ----
    @property
    def embedding(self):
        return self._lazy("embedding", self._create_embedding)

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

    # ---- Auth ----
    @property
    def auth(self):
        from mellow.auth.jwt_auth import JWTAuthProvider
        return self._lazy("auth", lambda: JWTAuthProvider(self._settings))

    # ---- Agent ----
    @property
    def agent(self):
        return self._lazy("agent", self._create_agent)

    def _create_agent(self):
        from mellow.agent.orchestrator import OrchestratorAgent
        from mellow.agent.chat_agent import ChatAgent
        from mellow.agent.teach_agent import TeachAgent
        from mellow.agent.reflect_agent import ReflectAgent

        orchestrator = OrchestratorAgent(self.llm_router)
        orchestrator._set_agents(
            chat_agent=ChatAgent(self.llm),
            teach_agent=TeachAgent(self.llm),
            reflect_agent=ReflectAgent(self.llm),
        )
        return orchestrator

    # ---- Persona ----
    @property
    def persona_manager(self):
        from mellow.persona.manager import PersonaManager
        return self._lazy("persona_manager", lambda: PersonaManager(self._settings))

    # ---- Memory ----
    @property
    def profile_manager(self):
        from mellow.memory.learning_profile import LearningProfileManager
        return self._lazy("profile_manager", lambda: LearningProfileManager())

    @property
    def memory_manager(self):
        from mellow.memory.persona_memory import PersonaMemoryManager
        return self._lazy("memory_manager", lambda: PersonaMemoryManager())

    # ---- Voice (Phase 8) ----
    # @property
    # def asr(self): ...
    # @property
    # def tts(self): ...


async def get_container() -> AsyncGenerator[Container, None]:
    yield Container.instance()
