from ai_code_agent.schemas import Field, BaseModel, Literal


class FileModification(BaseModel):

    updated_content: str = Field(
        description="Complete final file content with all review issues fixed."
    )

    summary: str = Field(
        description="Summary of fixes applied and review issues resolved."
    )


class GeneratedChanges(BaseModel):
    action: Literal["modify", "create"]
    updated_content: str
    summary: str
