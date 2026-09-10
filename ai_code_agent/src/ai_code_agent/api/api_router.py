from ai_code_agent.api import (
    APIRouter,
    user_route,
    auth_route,
    repositories_route,
    chats_route,
)

root_router = APIRouter()

root_router.include_router(user_route, tags=["Users"])
root_router.include_router(auth_route, tags=["Auth"])
root_router.include_router(repositories_route, tags=["Repositories"])
root_router.include_router(chats_route, tags=["Chats"])
