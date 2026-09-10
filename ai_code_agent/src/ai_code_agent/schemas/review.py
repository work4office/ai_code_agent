from ai_code_agent.schemas import Field, BaseModel, Literal


class ReviewIssue(BaseModel):
    file_path: str | None = None
    issue: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = "medium"
    recommended_fix: str


class ReviewResult(BaseModel):
    review_score: float = Field(default=0)
    passed: bool = Field(default=False)
    summary: str = Field(default="")
    issues: list[ReviewIssue] = Field(default_factory=list)
