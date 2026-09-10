from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    os,
    create_backup,
    write_file,
    coerce_generated_change,
)


async def apply_changes_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    applied_files = []

    for file_path, value in state["generated_changes"].items():
        change = coerce_generated_change(value)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        await create_backup(file_path, state["directory_path"])

        await write_file(file_path, change.updated_content)

        applied_files.append(file_path)
    end_time = time.perf_counter()
    print("apply_changes_node: ", end_time - start_time)
    return {
        **state,
        "applied_files": applied_files,
    }
