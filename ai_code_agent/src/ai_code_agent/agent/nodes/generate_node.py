from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    os,
    CODE_MODIFIER_PROMPT,
    cast,
    GeneratedChanges,
    FileModification,
    get_goggle_llm,
    resolve_agent_file_path,
    read_file,
)

llm = get_goggle_llm()


async def generate_changes_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    implementation_plan = state["implementation_plan"]
    for file_change in implementation_plan.file_changes:

        resolved_file_path = resolve_agent_file_path(
            state["directory_path"], file_change.path
        )

        action = "modify" if os.path.exists(resolved_file_path) else "create"

        if action == "modify":
            current_content = await read_file(resolved_file_path)
        else:
            current_content = ""

        prompt = CODE_MODIFIER_PROMPT.format(
            user_request=state["user_request"],
            implementation_plan=implementation_plan.model_dump_json(indent=2),
            file_path=resolved_file_path,
            file_action=action,
            file_content=current_content,
        )

        response = cast(
            FileModification,
            await llm.with_structured_output(FileModification).ainvoke(prompt),
        )

        generated_changes[resolved_file_path] = GeneratedChanges(
            action=action,
            updated_content=response.updated_content,
            summary=response.summary,
        )
    end_time = time.perf_counter()
    print("generate_changes_node: ", end_time - start_time)
    return {**state, "generated_changes": generated_changes, "retry_count": 1}
