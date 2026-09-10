from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    asyncio,
    get_generated_diffs,
    interrupt,
)


def human_approval_node(state: AgentState):
    start_time = time.perf_counter()
    diffs = asyncio.run(get_generated_diffs(state["generated_changes"]))
    payload = {
        "file_changes": state["implementation_plan"].file_changes,
        "implementation_plan": state["implementation_plan"],
        "diffs": diffs,
        "review": state["review_result"],
    }

    approved = interrupt(payload)
    end_time = time.perf_counter()
    print("human_approval_node: ", end_time - start_time)
    return {**state, "approved": bool(approved)}
