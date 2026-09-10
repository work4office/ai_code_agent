from ai_code_agent.agent import (
    AgentState,
    Literal,
    StateGraph,
    START,
    END,
    GeneratedChanges,
    ImplementationPlan,
    ReviewResult,
    JsonPlusSerializer,
    MemorySaver,
)
from ai_code_agent.agent.nodes.index_node import index_node
from ai_code_agent.agent.nodes.retrieve_node import retrieve_node
from ai_code_agent.agent.nodes.scan_node import scan_node
from ai_code_agent.agent.nodes.analyze_node import analyze_node
from ai_code_agent.agent.nodes.plan_node import plan_node
from ai_code_agent.agent.nodes.generate_node import generate_changes_node
from ai_code_agent.agent.nodes.improve_node import improve_node
from ai_code_agent.agent.nodes.apply_changes_node import apply_changes_node
from ai_code_agent.agent.nodes.approval_node import human_approval_node
from ai_code_agent.agent.nodes.review_node import review_node


def review_router(state: AgentState) -> Literal["human_approval", "improve"]:
    print(state["review_result"].review_score)
    if state["review_result"].review_score > 7 or state["retry_count"] >= 3:
        return "human_approval"

    return "improve"


def approval_router(state: AgentState) -> Literal["apply", "end"]:

    if state["approved"]:
        return "apply"

    return "end"


def build_graph():
    graph = StateGraph(AgentState)

    # graph.add_node("scan", scan_node)
    # graph.add_node("index", index_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("plan", plan_node)
    graph.add_node("generate_changes", generate_changes_node)
    graph.add_node("review", review_node)
    graph.add_node("improve", improve_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("apply_changes", apply_changes_node)

    # graph.add_edge(START, "scan")
    # graph.add_edge("scan", "index")
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "analyze")
    graph.add_edge("analyze", "plan")
    graph.add_edge("plan", "generate_changes")
    graph.add_edge("generate_changes", "review")

    graph.add_conditional_edges(
        "review",
        review_router,
        {
            "human_approval": "human_approval",
            "improve": "improve",
        },
    )

    graph.add_edge("improve", "review")

    graph.add_conditional_edges(
        "human_approval", approval_router, {"apply": "apply_changes", "end": END}
    )

    graph.add_edge("apply_changes", END)

    # Create a serializer that explicitly allows your custom schema
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[GeneratedChanges, ImplementationPlan, ReviewResult]
    )

    # Wire the serde into checkpointer
    checkpointer = MemorySaver(serde=serde)
    return graph.compile(checkpointer=checkpointer)
