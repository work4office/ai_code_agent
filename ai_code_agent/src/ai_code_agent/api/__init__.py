from ai_code_agent.routes.user import router as user_route
from ai_code_agent.routes.auth import router as auth_route
from ai_code_agent.routes.repositories import router as repositories_route
from ai_code_agent.routes.chat import router as chats_route
from fastapi import APIRouter

__all__ = ["APIRouter", "user_route", "auth_route", "repositories_route", "chats_route"]
