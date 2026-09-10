from ai_code_agent.agent.nodes import AgentState, time, index_codebase


async def index_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    await index_codebase(
        file_paths=state["project_files"], collection_name=state["collection_name"]
    )
    end_time = time.perf_counter()
    print("index_node: ", end_time - start_time)
    return state
