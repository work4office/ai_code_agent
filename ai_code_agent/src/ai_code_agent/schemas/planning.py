from ai_code_agent.schemas import Field, BaseModel


class PlannedFileChange(BaseModel):
    path: str = Field(
        description="Relative or absolute file path. Use real file names. Do not use placeholders unless project name is unknown."
    )

    reason: str = Field(description="Why this file is required.")


class ImplementationPlan(BaseModel):
    file_changes: list[PlannedFileChange] = Field(default_factory=list)
    implementation_steps: list[str] = Field(default_factory=list)
