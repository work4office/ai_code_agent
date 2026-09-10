from ai_code_agent.schemas import BaseModel


class CodeChanges(BaseModel):
    id: int
    old_code: str
    updated_code: str
    file_path: str


class ChatResponse(BaseModel):
    changes: list[CodeChanges]
    message: str


class ChatRequest(BaseModel):
    user_request: str
    project_id: str


class ChatConfirmRequest(BaseModel):
    is_confirmed: bool
    project_id: str


class ChatConfirmResponse(BaseModel):
    status: str
    approved: bool
    applied_files: list[str]
