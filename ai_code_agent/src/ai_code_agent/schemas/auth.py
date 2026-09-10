from ai_code_agent.schemas import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    user: User


class TokenData(BaseModel):
    email: EmailStr | None = None
