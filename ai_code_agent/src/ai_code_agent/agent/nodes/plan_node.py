from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    PLAN_PROMPT,
    cast,
    ImplementationPlan,
    get_goggle_llm,
)

llm = get_goggle_llm()


async def plan_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    prompt = PLAN_PROMPT.format(analysis=state["analysis"])

    response = cast(
        ImplementationPlan,
        await llm.with_structured_output(ImplementationPlan).ainvoke(prompt),
    )
    end_time = time.perf_counter()
    print("plan_node: ", end_time - start_time)
    return {**state, "implementation_plan": response}
