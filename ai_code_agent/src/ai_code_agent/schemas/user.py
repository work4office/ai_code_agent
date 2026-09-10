from ai_code_agent.schemas import Field, BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str  # Used strictly on input registration


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read ORM models
