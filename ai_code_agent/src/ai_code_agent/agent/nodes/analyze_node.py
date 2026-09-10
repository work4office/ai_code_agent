from ai_code_agent.agent.nodes import AgentState, time, ANALYSIS_PROMPT, get_goggle_llm

llm = get_goggle_llm()


async def analyze_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    prompt = ANALYSIS_PROMPT.format(
        user_request=state["user_request"], retrieved_context=state["retrieved_context"]
    )

    response = await llm.ainvoke(prompt)
    end_time = time.perf_counter()
    print("analyze_node: ", end_time - start_time)
    return {**state, "analysis": response.content}  # type: ignore
