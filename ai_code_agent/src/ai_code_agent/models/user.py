from ai_code_agent.models import (
    SQLModel,
    Field,
    String,
    Column,
    Relationship,
    List,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from ai_code_agent.models.repositories import Repositories


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    email: str = Field(
        sa_column=Column(String(255), index=True, unique=True, nullable=False)
    )
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)

    repositories: List["Repositories"] = Relationship(back_populates="user")
