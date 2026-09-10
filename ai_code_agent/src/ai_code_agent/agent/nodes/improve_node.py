from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    IMPROVE_PROMPT,
    cast,
    FileModification,
    get_goggle_llm,
    GeneratedChanges,
)

llm = get_goggle_llm()


async def improve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    for file_path, change in state["generated_changes"].items():
        file_issues = []

        for review_file in state["review_result"].issues:
            if review_file.file_path is None or review_file.file_path == file_path:
                file_issues.append(review_file)

        if not file_issues:
            generated_changes[file_path] = change
            continue

        prompt = IMPROVE_PROMPT.format(
            user_request=state["user_request"],
            file_path=file_path,
            generated_changes=change.updated_content,
            review_score=state["review_result"].review_score,
            review_summary=state["review_result"].summary,
            review_issues="\n".join(
                f"[{issue.severity}] {issue.issue}" for issue in file_issues
            ),
        )
        response = cast(
            FileModification,
            await llm.with_structured_output(FileModification).ainvoke(prompt),
        )
        generated_changes[file_path] = GeneratedChanges(
            action=change.action,
            updated_content=response.updated_content,
            summary=response.summary,
        )
    end_time = time.perf_counter()
    print("improve_node: ", end_time - start_time)
    return {
        **state,
        "generated_changes": generated_changes,
        "retry_count": state.get("retry_count", 0) + 1,
    }
