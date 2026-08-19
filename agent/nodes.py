import asyncio
import json
import os
import time
from typing import cast

from agent.schemas import (
    GeneratedChanges,
    ImplementationPlan,
    FileModification,
    ReviewResult,
    ReviewIssue,
)
from agent.state import AgentState
from tools.utils import (
    coerce_review_result,
    generate_diff,
    coerce_generated_change,
    generate_review_context,
    get_generated_diffs,
)
from tools.file_tools import create_backup, scan_directory, read_file, write_file
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


async def index_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    await index_codebase(
        file_paths=state["project_files"], directory_path=state["directory_path"]
    )
    end_time = time.perf_counter()
    print("index_node: ", end_time - start_time)
    return state


def retrieve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    context = retrieve_relevant_code(
        user_request=state["user_request"], directory_path=state["directory_path"]
    )
    end_time = time.perf_counter()
    print("retrieve_node: ", end_time - start_time)
    return {**state, "retrieved_context": context["retrieved_documents"]}


async def analyze_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    prompt = ANALYSIS_PROMPT.format(
        user_request=state["user_request"], retrieved_context=state["retrieved_context"]
    )

    response = await llm.ainvoke(prompt)
    end_time = time.perf_counter()
    print("analyze_node: ", end_time - start_time)
    return {**state, "analysis": response.content}  # type: ignore


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


async def generate_changes_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    implementation_plan = state["implementation_plan"]
    for file_change in implementation_plan.file_changes:

        resolved_file_path = resolve_agent_file_path(
            state["directory_path"], file_change.path
        )

        action = "modify" if os.path.exists(resolved_file_path) else "create"

        if action == "modify":
            current_content = await read_file(resolved_file_path)
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
            await llm.with_structured_output(FileModification).ainvoke(prompt),
        )

        generated_changes[resolved_file_path] = GeneratedChanges(
            action=action,
            updated_content=response.updated_content,
            summary=response.summary,
        )
    end_time = time.perf_counter()
    print("generate_changes_node: ", end_time - start_time)
    return {**state, "generated_changes": generated_changes, "retry_count": 1}


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


async def improve_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    generated_changes: dict[str, GeneratedChanges] = {}

    for file_path, change in state["generated_changes"].items():
        file_issues = []

        for review_file in state["review_result"].issues:
            if review_file.file_path is None or review_file.file_path == file_path:
                file_issues.append(review_file)

        if not file_issues:
            generated_changes[file_path] = change
            continue

        prompt = IMPROVE_PROMPT.format(
            user_request=state["user_request"],
            file_path=file_path,
            generated_changes=change.updated_content,
            review_score=state["review_result"].review_score,
            review_summary=state["review_result"].summary,
            review_issues="\n".join(
                f"[{issue.severity}] {issue.issue}" for issue in file_issues
            ),
        )
        response = cast(
            FileModification,
            await llm.with_structured_output(FileModification).ainvoke(prompt),
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
