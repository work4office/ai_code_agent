import os
import aiofiles

from fastapi import APIRouter, status, HTTPException, Depends, Response, Request

from ai_code_agent.database.session import SessionDep
from ai_code_agent.models.user import Users
from ai_code_agent.models.repositories import Repositories

from ai_code_agent.schemas.user import UserCreate, UserResponse
from ai_code_agent.schemas.auth import Token, LoginRequest
from ai_code_agent.schemas.chat import (
    ChatResponse,
    ChatRequest,
    ChatConfirmResponse,
    ChatConfirmRequest,
)
from ai_code_agent.schemas.repositories import (
    RepositoryRequest,
    FileNode,
    IngestRepoResponse,
    FileContentResponse,
    ProjectResponse,
)

from sqlmodel import select
from datetime import timedelta

from typing import Annotated

from ai_code_agent.core.settings import settings
from ai_code_agent.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_refresh_user,
    setRefreshToken,
    deleteRefreshToken,
    get_current_user,
)

from ai_code_agent.services.graph_service import GraphService
from ai_code_agent.services.indexing_service import IndexingService
from ai_code_agent.services.git_service import GitService
from ai_code_agent.services.repository_service import RepositoryService
from ai_code_agent.services.file_service import build_tree

__all__ = [
    "APIRouter",
    "status",
    "SessionDep",
    "Users",
    "UserCreate",
    "UserResponse",
    "HTTPException",
    "select",
    "timedelta",
    "Token",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "settings",
    "LoginRequest",
    "get_current_refresh_user",
    "setRefreshToken",
    "deleteRefreshToken",
    "Depends",
    "Response",
    "Annotated",
    "RepositoryRequest",
    "IndexingService",
    "GitService",
    "RepositoryService",
    "get_current_user",
    "FileNode",
    "IngestRepoResponse",
    "build_tree",
    "aiofiles",
    "os",
    "FileContentResponse",
    "ProjectResponse",
    "GraphService",
    "ChatResponse",
    "ChatRequest",
    "ChatConfirmResponse",
    "Request",
    "Repositories",
    "ChatConfirmRequest",
]
