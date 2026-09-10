__version__ = "1.0.0"

from fastapi import FastAPI
from .core.lifespan import lifespan
from .api.api_router import root_router
from ai_code_agent.middleware.register_middleware import register_middleware

__all__ = ["FastAPI", "lifespan", "root_router", "register_middleware"]
