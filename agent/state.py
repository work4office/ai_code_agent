from typing import TypedDict

from agent.schemas import GeneratedChanges, ImplementationPlan, ReviewResult


class AgentState(TypedDict):

    directory_path: str
    user_request: str

    project_files: list[str]

    retrieved_context: str
    retrieved_files: dict[str, str]

    analysis: str

    implementation_plan: ImplementationPlan

    generated_changes: dict[str, GeneratedChanges]

    review_result: ReviewResult
    approved: bool
    applied_files: list[str]

    test_result: str
    retry_count: int
    final_summary: str
