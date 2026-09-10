from ai_code_agent.agent.nodes import AgentState, time, retrieve_relevant_code


def retrieve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    context = retrieve_relevant_code(
        user_request=state["user_request"], collection_name=state["collection_name"]
    )
    end_time = time.perf_counter()
    print("retrieve_node: ", end_time - start_time)
    return {**state, "retrieved_context": context["retrieved_documents"]}
