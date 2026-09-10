from ai_code_agent.agent.nodes import AgentState, time, scan_directory


def scan_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    files = scan_directory(state["directory_path"])
    end_time = time.perf_counter()
    print("scan_node: ", end_time - start_time)
    return {**state, "project_files": files}
