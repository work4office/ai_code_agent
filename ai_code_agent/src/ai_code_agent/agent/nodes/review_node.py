from ai_code_agent.agent.nodes import (
    AgentState,
    time,
    REVIEW_PROMPT,
    coerce_review_result,
    ReviewResult,
    get_goggle_llm,
    generate_review_context,
    ReviewIssue,
)

llm = get_goggle_llm()


async def review_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()

    review_context = await generate_review_context(state["generated_changes"])

    prompt = REVIEW_PROMPT.format(
        user_request=state["user_request"],
        implementation_plan=state["implementation_plan"].model_dump_json(indent=2),
        review_context=review_context,
    )
    try:
        response = await llm.with_structured_output(ReviewResult).ainvoke(prompt)
        review_result = coerce_review_result(response)
    except Exception as exc:
        review_result = ReviewResult(
            review_score=0,
            summary="The review could not be completed with valid structured output.",
            passed=False,
            issues=[
                ReviewIssue(
                    file_path=None,
                    issue=f"Malformed review output: {exc}",
                    recommended_fix="",
                )
            ],
        )
    end_time = time.perf_counter()
    print("review_node: ", end_time - start_time)
    return {**state, "review_result": review_result}
