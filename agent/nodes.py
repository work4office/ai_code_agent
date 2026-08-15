import os
import time
from typing import cast

from agent.schemas import (
    GeneratedChanges,
    ImplementationPlan,
    FileModification,
    ReviewResult,
)
from agent.state import AgentState
from tools.utils import (
    coerce_review_result,
    generate_diff,
    coerce_generated_change,
)
from tools.file_tools import scan_directory, read_file, write_file
from tools.code_indexer import index_codebase
from tools.path_resolver import resolve_agent_file_path
from tools.retriever import retrieve_relevant_code
from langgraph.types import interrupt
from models.llm import get_llm, get_goggle_llm
from agent.prompts import (
    ANALYSIS_PROMPT,
    PLAN_PROMPT,
    REVIEW_PROMPT,
    CODE_MODIFIER_PROMPT,
    IMPROVE_PROMPT,
)

llm = get_goggle_llm()


def scan_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    files = scan_directory(state["directory_path"])
    end_time = time.perf_counter()
    print("scan_node: ", end_time - start_time)
    return {**state, "project_files": files}


def index_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    index_codebase(state["project_files"])
    end_time = time.perf_counter()
    print("index_node: ", end_time - start_time)
    return state


def retrieve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    context = retrieve_relevant_code(state["user_request"])
    end_time = time.perf_counter()
    print("retrieve_node: ", end_time - start_time)
    return {**state, "retrieved_context": context["retrieved_documents"]}


def analyze_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    prompt = ANALYSIS_PROMPT.format(
        user_request=state["user_request"], retrieved_context=state["retrieved_context"]
    )

    response = llm.invoke(prompt)
    end_time = time.perf_counter()
    print("analyze_node: ", end_time - start_time)
    return {**state, "analysis": response.content}  # type: ignore


def plan_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    prompt = PLAN_PROMPT.format(analysis=state["analysis"])

    response = cast(
        ImplementationPlan,
        llm.with_structured_output(ImplementationPlan).invoke(prompt),
    )
    end_time = time.perf_counter()
    print("plan_node: ", end_time - start_time)
    return {**state, "implementation_plan": response}


def generate_changes_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    implementation_plan = state["implementation_plan"]
    print("implementation_plan.file_changes length: ", len(implementation_plan.file_changes))
    counter = 0
    for file_change in implementation_plan.file_changes:

        resolved_file_path = resolve_agent_file_path(
            state["directory_path"], file_change.path
        )

        action = "modify" if os.path.exists(resolved_file_path) else "create"

        if action == "modify":
            current_content = read_file(resolved_file_path)
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
            llm.with_structured_output(FileModification).invoke(prompt),
        )

        generated_changes[resolved_file_path] = GeneratedChanges(
            action=action,
            updated_content=response.updated_content,
            summary=response.summary,
        )
        counter += 1
        print("generated_changes count: ",counter)
    end_time = time.perf_counter()
    print("generate_changes_node: ", end_time - start_time)
    return {**state, "generated_changes": generated_changes, "retry_count": 1}


def generate_diff_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_diffs = {}

    for file_path, change in state["generated_changes"].items():

        if change.action == "modify":
            original_content = read_file(file_path)
        else:
            original_content = ""

        diff = generate_diff(
            file_path=file_path,
            old_content=original_content,
            new_content=change.updated_content,
        )
        if diff:
            generated_diffs[file_path] = diff
    end_time = time.perf_counter()
    print("generate_diff_node: ", end_time - start_time)
    return {**state, "generated_diffs": generated_diffs}


def review_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    combined_diff = "\n\n".join(state["generated_diffs"].values())

    prompt = REVIEW_PROMPT.format(
        user_request=state["user_request"],
        implementation_plan=state["implementation_plan"],
        generated_changes=state["generated_changes"],
        generated_diffs=combined_diff,
    )
    try:
        response = llm.with_structured_output(ReviewResult).invoke(prompt)
        review_result = coerce_review_result(response)
    except Exception as exc:
        review_result = ReviewResult(
            review_score=0,
            summary="The review could not be completed with valid structured output.",
            issues=[f"Malformed review output: {exc}"],
        )
    end_time = time.perf_counter()
    print("review_node: ", end_time - start_time)
    return {**state, "review_result": review_result}


def improve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    for file_path, change in state["generated_changes"].items():
        prompt = IMPROVE_PROMPT.format(
            user_request=state["user_request"],
            file_path=file_path,
            generated_changes=change,
            review_score=state["review_result"].review_score,
            review_summary=state["review_result"].summary,
            review_issues=state["review_result"].issues,
        )
        response = cast(
            FileModification,
            llm.with_structured_output(FileModification).invoke(prompt),
        )
        generated_changes[file_path] = GeneratedChanges(
            action=change.action,
            updated_content=response.updated_content,
            summary=response.summary,
        )
    end_time = time.perf_counter()
    print("improve_node: ", end_time - start_time)
    return {
        **state,
        "generated_changes": generated_changes,
        "retry_count": state.get("retry_count", 0) + 1,
    }


def human_approval_node(state: AgentState):
    start_time = time.perf_counter()
    payload = {
        "file_changes": state["implementation_plan"].file_changes,
        "implementation_plan": state["implementation_plan"],
        "diffs": state["generated_diffs"],
        "review": state["review_result"],
    }

    approved = interrupt(payload)
    end_time = time.perf_counter()
    print("human_approval_node: ", end_time - start_time)
    return {**state, "approved": bool(approved)}


def apply_changes_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    applied_files = []

    for file_path, value in state["generated_changes"].items():
        change = coerce_generated_change(value)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            backup_path = file_path + ".agent.backup"

            original = read_file(file_path)
            write_file(backup_path, original)

        write_file(file_path, change.updated_content)

        applied_files.append(file_path)
    end_time = time.perf_counter()
    print("apply_changes_node: ", end_time - start_time)
    return {
        **state,
        "applied_files": applied_files,
    }
