from ai_code_agent.models import (
    SQLModel,
    Field,
    String,
    Column,
    Relationship,
    datetime,
    timezone,
    TYPE_CHECKING,
    Optional,
)

if TYPE_CHECKING:
    from ai_code_agent.models.user import Users


class Repositories(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    repo_name: str = Field(sa_column=Column(String(255), nullable=False))
    repo_url: str = Field(sa_column=Column(String(255), nullable=False))
    commit_hash: str = Field(sa_column=Column(String(255), nullable=False))
    collection_name: str = Field(sa_column=Column(String(255), nullable=False))
    indexed_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    user: "Users" = Relationship(back_populates="repositories")
