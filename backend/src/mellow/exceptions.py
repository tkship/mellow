"""自定义异常 —— 统一的错误类型和 FastAPI 全局异常处理。"""

from fastapi import Request
from fastapi.responses import JSONResponse


class MellowError(Exception):
    """Mellow 基础异常。"""

    def __init__(self, message: str, status_code: int = 500, detail: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class AuthenticationError(MellowError):
    """认证相关错误。"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status_code=401)


class AuthorizationError(MellowError):
    """权限不足。"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status_code=403)


class NotFoundError(MellowError):
    """资源不存在。"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=404)


class ValidationError(MellowError):
    """业务校验失败。"""

    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message, status_code=422)


class LLMError(MellowError):
    """LLM 调用失败。"""

    def __init__(self, message: str = "AI 服务暂时不可用"):
        super().__init__(message, status_code=503)


class KnowledgeError(MellowError):
    """知识库查询失败。"""

    def __init__(self, message: str = "知识库查询失败"):
        super().__init__(message, status_code=502)


async def mellow_exception_handler(request: Request, exc: MellowError) -> JSONResponse:
    """全局异常处理器 —— 将所有 MellowError 转为统一 JSON 响应。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "detail": exc.detail,
        },
    )
