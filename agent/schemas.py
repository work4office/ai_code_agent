from typing import Literal

from pydantic import BaseModel, Field


class FileModification(BaseModel):

    updated_content: str = Field(
        description="Complete final file content with all review issues fixed."
    )

    summary: str = Field(
        description="Summary of fixes applied and review issues resolved."
    )


class FileSelection(BaseModel):
    files: list[str] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    file_path: str | None = None
    issue: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = "medium"


class ReviewResult(BaseModel):
    review_score: float = Field(default=0)
    summary: str = Field(default="")
    issues: list[ReviewIssue] = Field(default_factory=list)


class PlannedFileChange(BaseModel):
    path: str = Field(
        description="Relative or absolute file path. Use real file names. Do not use placeholders unless project name is unknown."
    )

    reason: str = Field(description="Why this file is required.")


class ImplementationPlan(BaseModel):
    file_changes: list[PlannedFileChange] = Field(default_factory=list)
    implementation_steps: list[str] = Field(default_factory=list)


class GeneratedChanges(BaseModel):
    action: Literal["modify", "create"]
    updated_content: str
    summary: str
