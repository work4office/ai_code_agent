# AI Code Agent: End-to-End LangGraph Tool Calling with Human Approval and Pull Request Creation

## 1. Objective

This guide implements a complete LangGraph workflow for the request:

> Fix the authentication issue and raise a pull request.

The workflow:

1. Extracts structured intent from the user request.
2. Analyzes the repository.
3. Produces an implementation plan.
4. Generates proposed file changes.
5. Reviews those changes.
6. Interrupts the graph for human approval.
7. Resumes the same graph thread from a FastAPI endpoint.
8. Applies the approved changes.
9. Runs validation.
10. Creates and pushes a Git branch.
11. Lets an LLM request the `create_pull_request` tool.
12. Executes the tool through LangGraph `ToolNode`.
13. Returns the PR URL in the final response.

The key distinction is:

```text
Deterministic graph edge:
prepare_git -> create_pr_node

Actual tool calling:
LLM.bind_tools(...) -> AIMessage.tool_calls -> ToolNode -> ToolMessage
```

---

## 2. Recommended project structure

```text
app/
├── api/
│   ├── dependencies.py
│   └── routes/
│       └── agent.py
├── agent/
│   ├── graph.py
│   ├── models.py
│   ├── nodes.py
│   ├── prompts.py
│   ├── state.py
│   └── tools.py
├── core/
│   └── config.py
├── schemas/
│   └── agent.py
├── services/
│   ├── github_service.py
│   ├── project_service.py
│   └── validation_service.py
└── main.py
```

---

## 3. Dependencies

```bash
pip install fastapi uvicorn langchain langgraph langchain-openai \
    pydantic pydantic-settings httpx gitpython
```

Use a persistent LangGraph checkpointer in production. A memory checkpointer is included here so the example remains focused and executable.

---

## 4. Environment configuration

Create `.env`:

```env
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4.1-mini
GITHUB_TOKEN=your-github-token
GITHUB_API_URL=https://api.github.com
REPOSITORY_ROOT=/absolute/path/to/local/repository
```

### `app/core/config.py`

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    github_token: str
    github_api_url: str = "https://api.github.com"
    repository_root: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 5. API schemas

### `app/schemas/agent.py`

```python
from typing import Any

from pydantic import BaseModel, Field


class StartAgentRequest(BaseModel):
    chat_id: str = Field(min_length=1)
    user_request: str = Field(min_length=1)
    repository: str = Field(
        description="GitHub repository in owner/name format"
    )
    base_branch: str = "main"


class ApprovalRequest(BaseModel):
    chat_id: str = Field(min_length=1)
    approved: bool


class AgentResponse(BaseModel):
    status: str
    data: dict[str, Any]
```

---

## 6. Structured intent model

### `app/agent/models.py`

```python
from typing import Literal

from pydantic import BaseModel, Field


RequestedAction = Literal[
    "analyze_code",
    "modify_code",
    "apply_changes",
    "create_pr",
]


class RequestIntent(BaseModel):
    task_summary: str = Field(
        description="Concise technical summary of the requested change"
    )
    requested_actions: list[RequestedAction]
    requires_code_change: bool
    pr_title: str | None = None


class FileChange(BaseModel):
    relative_path: str
    operation: Literal["create", "update", "delete"]
    new_content: str | None = None
    explanation: str


class GeneratedChanges(BaseModel):
    changes: list[FileChange]


class ReviewResult(BaseModel):
    approved: bool
    summary: str
    issues: list[str] = []
```

---

## 7. LangGraph state

### `app/agent/state.py`

```python
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from app.agent.models import FileChange, RequestedAction


class AgentState(TypedDict, total=False):
    # ToolNode reads and writes this field.
    messages: Annotated[list[AnyMessage], add_messages]

    chat_id: str
    user_request: str
    repository: str
    repository_root: str
    base_branch: str

    task_summary: str
    requested_actions: list[RequestedAction]
    requires_code_change: bool

    repository_context: str
    implementation_plan: str
    generated_changes: list[FileChange]
    review_summary: str
    review_issues: list[str]

    approval_granted: bool
    changes_applied: bool
    tests_passed: bool
    validation_output: str

    working_branch: str
    commit_message: str
    commit_sha: str
    branch_pushed: bool

    pr_title: str
    pr_description: str
    pr_url: str
    pr_number: int

    completed_tool_calls: list[str]
    final_answer: str
    error: str

    # Optional arbitrary metadata.
    metadata: dict[str, Any]
```

---

## 8. Repository service

This service performs deterministic local file operations. It rejects paths outside the configured repository root.

### `app/services/project_service.py`

```python
from pathlib import Path

from app.agent.models import FileChange


class ProjectService:
    def __init__(self, repository_root: str):
        self.repository_root = Path(repository_root).resolve()

    def _safe_path(self, relative_path: str) -> Path:
        candidate = (self.repository_root / relative_path).resolve()

        try:
            candidate.relative_to(self.repository_root)
        except ValueError as exc:
            raise ValueError(
                f"Path escapes repository root: {relative_path}"
            ) from exc

        return candidate

    async def build_repository_context(self, max_files: int = 80) -> str:
        allowed_suffixes = {
            ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yml", ".yaml"
        }
        excluded_parts = {
            ".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"
        }

        sections: list[str] = []
        count = 0

        for path in self.repository_root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in excluded_parts for part in path.parts):
                continue
            if path.suffix.lower() not in allowed_suffixes:
                continue

            relative_path = path.relative_to(self.repository_root)

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            sections.append(
                f"FILE: {relative_path}\n```\n{content[:12000]}\n```"
            )
            count += 1

            if count >= max_files:
                break

        return "\n\n".join(sections)

    async def apply_changes(self, changes: list[FileChange]) -> None:
        for change in changes:
            path = self._safe_path(change.relative_path)

            if change.operation == "delete":
                if path.exists():
                    path.unlink()
                continue

            if change.new_content is None:
                raise ValueError(
                    f"new_content is required for {change.operation}: "
                    f"{change.relative_path}"
                )

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(change.new_content, encoding="utf-8")
```

---

## 9. Validation service

Adapt commands to the repository technology. Do not execute an LLM-generated shell command. Keep the allowed commands application-controlled.

### `app/services/validation_service.py`

```python
import asyncio
from dataclasses import dataclass


@dataclass
class ValidationResult:
    success: bool
    output: str


class ValidationService:
    def __init__(self, repository_root: str):
        self.repository_root = repository_root

    async def _run(self, *command: str) -> tuple[int, str]:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=self.repository_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        stdout, _ = await process.communicate()
        output = stdout.decode("utf-8", errors="replace")
        return process.returncode, output

    async def validate(self) -> ValidationResult:
        # Replace or extend this allowlisted validation pipeline as needed.
        return_code, output = await self._run(
            "python", "-m", "pytest", "-q"
        )

        return ValidationResult(
            success=return_code == 0,
            output=output,
        )
```

---

## 10. GitHub and Git service

This example uses GitPython for local branch/commit/push and `httpx` for GitHub PR creation.

### `app/services/github_service.py`

```python
from dataclasses import dataclass

import httpx
from git import Repo


@dataclass
class GitPreparationResult:
    branch_name: str
    commit_sha: str


@dataclass
class PullRequestResult:
    number: int
    url: str


class GitHubService:
    def __init__(
        self,
        token: str,
        api_url: str,
        repository_root: str,
    ):
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.repository_root = repository_root

    def _repo(self) -> Repo:
        return Repo(self.repository_root)

    async def prepare_and_push_branch(
        self,
        base_branch: str,
        branch_name: str,
        commit_message: str,
    ) -> GitPreparationResult:
        repo = self._repo()

        if repo.is_dirty(untracked_files=True) is False:
            raise ValueError("No repository changes are available to commit.")

        repo.git.checkout(base_branch)

        if branch_name in [head.name for head in repo.heads]:
            repo.git.checkout(branch_name)
        else:
            repo.git.checkout("-b", branch_name)

        repo.git.add(A=True)
        commit = repo.index.commit(commit_message)
        repo.git.push("--set-upstream", "origin", branch_name)

        return GitPreparationResult(
            branch_name=branch_name,
            commit_sha=commit.hexsha,
        )

    async def create_pull_request(
        self,
        repository: str,
        base_branch: str,
        working_branch: str,
        title: str,
        description: str,
    ) -> PullRequestResult:
        url = f"{self.api_url}/repos/{repository}/pulls"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        payload = {
            "title": title,
            "head": working_branch,
            "base": base_branch,
            "body": description,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return PullRequestResult(
            number=data["number"],
            url=data["html_url"],
        )
```

> Production note: branch creation, commits, and pushes are side effects. Add idempotency checks before retrying this node. Also ensure the remote uses a credential mechanism that does not expose tokens in logs.

---

## 11. Tool definition

This is an actual LangChain tool. The docstring and type annotations form the schema shown to the LLM.

### `app/agent/tools.py`

```python
from langchain_core.tools import BaseTool, tool

from app.services.github_service import GitHubService


def build_create_pull_request_tool(
    github_service: GitHubService,
) -> BaseTool:

    @tool("create_pull_request")
    async def create_pull_request(
        repository: str,
        base_branch: str,
        working_branch: str,
        title: str,
        description: str,
    ) -> dict:
        """Create a GitHub pull request from an existing pushed branch.

        Use this tool only when the user explicitly requested a pull request
        and application state confirms that human approval was granted,
        code changes were applied, validation passed, and the branch was
        committed and pushed.
        """

        result = await github_service.create_pull_request(
            repository=repository,
            base_branch=base_branch,
            working_branch=working_branch,
            title=title,
            description=description,
        )

        return {
            "pr_number": result.number,
            "pr_url": result.url,
        }

    return create_pull_request
```

---

## 12. Prompts

### `app/agent/prompts.py`

```python
INTENT_SYSTEM_PROMPT = """
You classify requests for an AI code agent.

Available actions:
- analyze_code
- modify_code
- apply_changes
- create_pr

Rules:
1. Include create_pr only when the user explicitly asks to create, open,
   or raise a pull request or PR.
2. A create_pr request implies analyze_code, modify_code, and apply_changes.
3. Do not execute any action.
4. Return only the requested structured output.
"""

PLAN_SYSTEM_PROMPT = """
You are a senior software engineer. Create a cautious implementation plan
from the user request and repository context. Mention files to inspect or
change, important constraints, validation, and compatibility concerns.
Do not claim that code has already been changed.
"""

IMPLEMENT_SYSTEM_PROMPT = """
You are implementing an approved engineering plan against the supplied
repository context. Return complete replacement content for every created
or updated file. Use relative paths only. Do not use '..' path traversal.
Do not include unrelated changes.
"""

REVIEW_SYSTEM_PROMPT = """
Review the proposed changes for correctness, security, maintainability,
compatibility, and alignment with the user request. Approve only if no
blocking issue remains.
"""

ACTION_SYSTEM_PROMPT = """
You are the post-approval action executor for an AI code agent.

You can call only the tools supplied to you. If a pull request was explicitly
requested and all verified prerequisites are true, call create_pull_request
exactly once with the supplied arguments. Never invent repository, branch,
title, or description values. If the tool result is already present, do not
call the tool again; provide a concise completion response instead.
"""
```

---

## 13. Graph nodes

### `app/agent/nodes.py`

```python
import json
import re
from collections.abc import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt

from app.agent.models import GeneratedChanges, RequestIntent, ReviewResult
from app.agent.prompts import (
    ACTION_SYSTEM_PROMPT,
    IMPLEMENT_SYSTEM_PROMPT,
    INTENT_SYSTEM_PROMPT,
    PLAN_SYSTEM_PROMPT,
    REVIEW_SYSTEM_PROMPT,
)
from app.agent.state import AgentState
from app.services.github_service import GitHubService
from app.services.project_service import ProjectService
from app.services.validation_service import ValidationService


def normalize_requested_actions(actions: list[str]) -> list[str]:
    normalized = list(dict.fromkeys(actions))

    if "create_pr" in normalized:
        for required in (
            "analyze_code",
            "modify_code",
            "apply_changes",
        ):
            if required not in normalized:
                normalized.append(required)

    return normalized


def create_analyze_node(llm: BaseChatModel) -> Callable:
    intent_llm = llm.with_structured_output(RequestIntent)

    async def analyze_node(state: AgentState) -> dict:
        result: RequestIntent = await intent_llm.ainvoke(
            [
                SystemMessage(content=INTENT_SYSTEM_PROMPT),
                HumanMessage(content=state["user_request"]),
            ]
        )

        actions = normalize_requested_actions(result.requested_actions)

        return {
            "task_summary": result.task_summary,
            "requested_actions": actions,
            "requires_code_change": result.requires_code_change,
            "pr_title": result.pr_title,
            "completed_tool_calls": [],
        }

    return analyze_node


def create_repository_context_node(
    project_service: ProjectService,
) -> Callable:
    async def repository_context_node(state: AgentState) -> dict:
        context = await project_service.build_repository_context()
        return {"repository_context": context}

    return repository_context_node


def create_plan_node(llm: BaseChatModel) -> Callable:
    async def plan_node(state: AgentState) -> dict:
        response = await llm.ainvoke(
            [
                SystemMessage(content=PLAN_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"User request:\n{state['user_request']}\n\n"
                        f"Repository context:\n{state['repository_context']}"
                    )
                ),
            ]
        )
        return {"implementation_plan": str(response.content)}

    return plan_node


def create_implement_node(llm: BaseChatModel) -> Callable:
    implementation_llm = llm.with_structured_output(GeneratedChanges)

    async def implement_node(state: AgentState) -> dict:
        result: GeneratedChanges = await implementation_llm.ainvoke(
            [
                SystemMessage(content=IMPLEMENT_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"User request:\n{state['user_request']}\n\n"
                        f"Implementation plan:\n{state['implementation_plan']}\n\n"
                        f"Repository context:\n{state['repository_context']}"
                    )
                ),
            ]
        )
        return {"generated_changes": result.changes}

    return implement_node


def create_review_node(llm: BaseChatModel) -> Callable:
    review_llm = llm.with_structured_output(ReviewResult)

    async def review_node(state: AgentState) -> dict:
        serialized_changes = [
            change.model_dump() for change in state["generated_changes"]
        ]

        result: ReviewResult = await review_llm.ainvoke(
            [
                SystemMessage(content=REVIEW_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"User request:\n{state['user_request']}\n\n"
                        f"Plan:\n{state['implementation_plan']}\n\n"
                        "Proposed changes:\n"
                        f"{json.dumps(serialized_changes, indent=2)}"
                    )
                ),
            ]
        )

        return {
            "review_summary": result.summary,
            "review_issues": result.issues,
            "error": None if result.approved else result.summary,
        }

    return review_node


async def request_approval_node(state: AgentState) -> dict:
    pending_actions = ["Apply the proposed repository changes"]

    if "create_pr" in state.get("requested_actions", []):
        pending_actions.extend(
            [
                "Run the allowlisted validation pipeline",
                "Create a Git branch",
                "Commit and push the approved changes",
                "Create a GitHub pull request",
            ]
        )

    response = interrupt(
        {
            "type": "code_change_approval",
            "message": "Review the proposed changes before execution.",
            "task_summary": state["task_summary"],
            "review_summary": state["review_summary"],
            "pending_actions": pending_actions,
            "changes": [
                change.model_dump()
                for change in state.get("generated_changes", [])
            ],
        }
    )

    approved = (
        response
        if isinstance(response, bool)
        else bool(response.get("approved", False))
    )

    return {"approval_granted": approved}


def create_apply_changes_node(
    project_service: ProjectService,
) -> Callable:
    async def apply_changes_node(state: AgentState) -> dict:
        if not state.get("approval_granted"):
            return {
                "changes_applied": False,
                "error": "Human approval was not granted.",
            }

        await project_service.apply_changes(state["generated_changes"])
        return {"changes_applied": True, "error": ""}

    return apply_changes_node


def create_validation_node(
    validation_service: ValidationService,
) -> Callable:
    async def validation_node(state: AgentState) -> dict:
        if not state.get("changes_applied"):
            return {
                "tests_passed": False,
                "validation_output": "Changes were not applied.",
            }

        result = await validation_service.validate()
        return {
            "tests_passed": result.success,
            "validation_output": result.output,
            "error": "" if result.success else "Validation failed.",
        }

    return validation_node


def slugify(value: str, maximum_length: int = 48) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:maximum_length] or "code-change"


def build_pr_description(state: AgentState) -> str:
    changed_files = "\n".join(
        f"- `{change.relative_path}`: {change.explanation}"
        for change in state.get("generated_changes", [])
    )

    return (
        "## Summary\n\n"
        f"{state['task_summary']}\n\n"
        "## Changed files\n\n"
        f"{changed_files}\n\n"
        "## Validation\n\n"
        "The configured validation pipeline completed successfully."
    )


def create_prepare_git_node(
    github_service: GitHubService,
) -> Callable:
    async def prepare_git_node(state: AgentState) -> dict:
        if "create_pr" not in state.get("requested_actions", []):
            return {}
        if not state.get("approval_granted"):
            raise ValueError("PR preparation requires human approval.")
        if not state.get("changes_applied"):
            raise ValueError("PR preparation requires applied changes.")
        if not state.get("tests_passed"):
            raise ValueError("PR preparation requires passing validation.")

        working_branch = f"ai-agent/{slugify(state['task_summary'])}"
        commit_message = f"fix: {state['task_summary']}"

        result = await github_service.prepare_and_push_branch(
            base_branch=state["base_branch"],
            branch_name=working_branch,
            commit_message=commit_message,
        )

        return {
            "working_branch": result.branch_name,
            "commit_message": commit_message,
            "commit_sha": result.commit_sha,
            "branch_pushed": True,
            "pr_title": state.get("pr_title")
            or f"Fix: {state['task_summary']}",
            "pr_description": build_pr_description(state),
        }

    return prepare_git_node


def create_post_approval_action_node(
    tool_enabled_llm: BaseChatModel,
) -> Callable:
    async def post_approval_action_node(state: AgentState) -> dict:
        if not state.get("approval_granted"):
            raise ValueError("Tool execution requires human approval.")
        if not state.get("changes_applied"):
            raise ValueError("Tool execution requires applied changes.")
        if not state.get("tests_passed"):
            raise ValueError("Tool execution requires passing validation.")
        if not state.get("branch_pushed"):
            raise ValueError("Tool execution requires a pushed branch.")

        action_context = HumanMessage(
            content=(
                "Complete the remaining explicitly requested action.\n\n"
                f"Requested actions: {state['requested_actions']}\n"
                f"Already completed tool calls: "
                f"{state.get('completed_tool_calls', [])}\n"
                f"Repository: {state['repository']}\n"
                f"Base branch: {state['base_branch']}\n"
                f"Working branch: {state['working_branch']}\n"
                f"Commit SHA: {state['commit_sha']}\n"
                f"PR title: {state['pr_title']}\n"
                f"PR description:\n{state['pr_description']}\n\n"
                "Verified prerequisites:\n"
                f"- approval_granted={state['approval_granted']}\n"
                f"- changes_applied={state['changes_applied']}\n"
                f"- tests_passed={state['tests_passed']}\n"
                f"- branch_pushed={state['branch_pushed']}"
            )
        )

        response = await tool_enabled_llm.ainvoke(
            [
                SystemMessage(content=ACTION_SYSTEM_PROMPT),
                *state.get("messages", []),
                action_context,
            ]
        )

        return {"messages": [response]}

    return post_approval_action_node


async def capture_tool_result_node(state: AgentState) -> dict:
    """Extract the PR result after ToolNode has appended ToolMessage."""

    last_message = state["messages"][-1]

    if not isinstance(last_message, ToolMessage):
        return {}

    if last_message.name != "create_pull_request":
        return {}

    try:
        payload = json.loads(last_message.content)
    except (TypeError, json.JSONDecodeError):
        payload = {}

    completed = list(state.get("completed_tool_calls", []))
    if "create_pull_request" not in completed:
        completed.append("create_pull_request")

    return {
        "pr_url": payload.get("pr_url", ""),
        "pr_number": payload.get("pr_number", 0),
        "completed_tool_calls": completed,
    }


async def rejected_node(state: AgentState) -> dict:
    return {
        "final_answer": "The proposed changes were not applied because approval was rejected."
    }


async def validation_failed_node(state: AgentState) -> dict:
    return {
        "final_answer": (
            "The changes were applied locally, but the validation pipeline "
            "failed. No branch was pushed and no pull request was created.\n\n"
            f"Validation output:\n{state.get('validation_output', '')}"
        )
    }


async def final_response_node(state: AgentState) -> dict:
    if state.get("pr_url"):
        answer = (
            "The approved changes were applied, validated, committed, "
            "pushed, and submitted as a pull request.\n\n"
            f"Pull request: {state['pr_url']}\n"
            f"Commit: {state.get('commit_sha', '')}"
        )
    elif state.get("changes_applied"):
        answer = "The approved changes were applied successfully."
    else:
        answer = (
            "The requested analysis and proposed changes are complete. "
            "No repository changes were applied."
        )

    return {"final_answer": answer}
```

---

## 14. Routing functions

### Add to `app/agent/nodes.py`

```python
from typing import Literal


def route_after_review(
    state: AgentState,
) -> Literal["request_approval", "final_response"]:
    if state.get("review_issues"):
        return "final_response"

    actions = state.get("requested_actions", [])
    if "apply_changes" in actions or "create_pr" in actions:
        return "request_approval"

    return "final_response"


def route_after_approval(
    state: AgentState,
) -> Literal["apply_changes", "rejected"]:
    return (
        "apply_changes"
        if state.get("approval_granted")
        else "rejected"
    )


def route_after_validation(
    state: AgentState,
) -> Literal["prepare_git", "final_response", "validation_failed"]:
    if not state.get("tests_passed"):
        return "validation_failed"

    if "create_pr" in state.get("requested_actions", []):
        return "prepare_git"

    return "final_response"


def route_after_action_llm(
    state: AgentState,
) -> Literal["tools", "final_response"]:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "final_response"
```

A custom router is used instead of sending `tools_condition` directly to `END`, because this graph has its own `final_response` node.

---

## 15. Build the graph

### `app/agent/graph.py`

```python
from functools import lru_cache

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes import (
    capture_tool_result_node,
    create_analyze_node,
    create_apply_changes_node,
    create_implement_node,
    create_plan_node,
    create_post_approval_action_node,
    create_prepare_git_node,
    create_repository_context_node,
    create_review_node,
    create_validation_node,
    final_response_node,
    rejected_node,
    request_approval_node,
    route_after_action_llm,
    route_after_approval,
    route_after_review,
    route_after_validation,
    validation_failed_node,
)
from app.agent.state import AgentState
from app.agent.tools import build_create_pull_request_tool
from app.core.config import get_settings
from app.services.github_service import GitHubService
from app.services.project_service import ProjectService
from app.services.validation_service import ValidationService


@lru_cache
def build_graph():
    settings = get_settings()

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    project_service = ProjectService(settings.repository_root)
    validation_service = ValidationService(settings.repository_root)
    github_service = GitHubService(
        token=settings.github_token,
        api_url=settings.github_api_url,
        repository_root=settings.repository_root,
    )

    create_pr_tool = build_create_pull_request_tool(github_service)
    tools = [create_pr_tool]

    # This binding enables the LLM to return AIMessage.tool_calls.
    tool_enabled_llm = llm.bind_tools(
        tools,
        parallel_tool_calls=False,
    )

    # This node executes the tool call requested by the LLM.
    tool_node = ToolNode(
        tools,
        handle_tool_errors=True,
    )

    builder = StateGraph(AgentState)

    builder.add_node("analyze", create_analyze_node(llm))
    builder.add_node(
        "repository_context",
        create_repository_context_node(project_service),
    )
    builder.add_node("plan", create_plan_node(llm))
    builder.add_node("implement", create_implement_node(llm))
    builder.add_node("review", create_review_node(llm))
    builder.add_node("request_approval", request_approval_node)
    builder.add_node(
        "apply_changes",
        create_apply_changes_node(project_service),
    )
    builder.add_node(
        "validate_changes",
        create_validation_node(validation_service),
    )
    builder.add_node(
        "prepare_git",
        create_prepare_git_node(github_service),
    )

    # LLM node that can request tools.
    builder.add_node(
        "post_approval_action",
        create_post_approval_action_node(tool_enabled_llm),
    )

    # Actual tool executor.
    builder.add_node("tools", tool_node)

    # Parse ToolMessage and store structured PR fields.
    builder.add_node("capture_tool_result", capture_tool_result_node)

    builder.add_node("final_response", final_response_node)
    builder.add_node("rejected", rejected_node)
    builder.add_node("validation_failed", validation_failed_node)

    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", "repository_context")
    builder.add_edge("repository_context", "plan")
    builder.add_edge("plan", "implement")
    builder.add_edge("implement", "review")

    builder.add_conditional_edges(
        "review",
        route_after_review,
        {
            "request_approval": "request_approval",
            "final_response": "final_response",
        },
    )

    builder.add_conditional_edges(
        "request_approval",
        route_after_approval,
        {
            "apply_changes": "apply_changes",
            "rejected": "rejected",
        },
    )

    builder.add_edge("apply_changes", "validate_changes")

    builder.add_conditional_edges(
        "validate_changes",
        route_after_validation,
        {
            "prepare_git": "prepare_git",
            "final_response": "final_response",
            "validation_failed": "validation_failed",
        },
    )

    builder.add_edge("prepare_git", "post_approval_action")

    # Actual dynamic tool-call routing.
    builder.add_conditional_edges(
        "post_approval_action",
        route_after_action_llm,
        {
            "tools": "tools",
            "final_response": "final_response",
        },
    )

    # ToolNode appends ToolMessage. Capture it, then return it to the LLM.
    builder.add_edge("tools", "capture_tool_result")
    builder.add_edge("capture_tool_result", "post_approval_action")

    builder.add_edge("final_response", END)
    builder.add_edge("rejected", END)
    builder.add_edge("validation_failed", END)

    # Replace MemorySaver with a persistent checkpointer for production.
    return builder.compile(checkpointer=MemorySaver())


graph = build_graph()
```

---

## 16. FastAPI routes

The start endpoint invokes the graph. When `interrupt()` is reached, LangGraph returns an interrupted result. The approval endpoint resumes the exact same graph thread using the same `chat_id` as `thread_id`.

### `app/api/routes/agent.py`

```python
from typing import Any

from fastapi import APIRouter, HTTPException
from langgraph.types import Command

from app.agent.graph import graph
from app.core.config import get_settings
from app.schemas.agent import (
    AgentResponse,
    ApprovalRequest,
    StartAgentRequest,
)


router = APIRouter(prefix="/agent", tags=["agent"])


def serialize_graph_result(result: dict[str, Any]) -> dict[str, Any]:
    # Adapt this serializer if your messages or Pydantic models need a
    # custom response shape for React.
    return result


@router.post("/start", response_model=AgentResponse)
async def start_agent(request: StartAgentRequest) -> AgentResponse:
    settings = get_settings()

    config = {
        "configurable": {
            "thread_id": request.chat_id,
        }
    }

    initial_state = {
        "messages": [],
        "chat_id": request.chat_id,
        "user_request": request.user_request,
        "repository": request.repository,
        "repository_root": settings.repository_root,
        "base_branch": request.base_branch,
    }

    try:
        result = await graph.ainvoke(
            initial_state,
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AgentResponse(
        status="completed_or_interrupted",
        data=serialize_graph_result(result),
    )


@router.post("/confirm", response_model=AgentResponse)
async def confirm_agent_action(
    request: ApprovalRequest,
) -> AgentResponse:
    config = {
        "configurable": {
            "thread_id": request.chat_id,
        }
    }

    try:
        result = await graph.ainvoke(
            Command(
                resume={
                    "approved": request.approved,
                }
            ),
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AgentResponse(
        status="completed",
        data=serialize_graph_result(result),
    )
```

---

## 17. FastAPI application

### `app/main.py`

```python
from fastapi import FastAPI

from app.api.routes.agent import router as agent_router


app = FastAPI(title="AI Code Agent")
app.include_router(agent_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

Run:

```bash
uvicorn app.main:app --reload
```

---

## 18. Request and resume examples

### Start the workflow

```bash
curl -X POST http://localhost:8000/agent/start \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "chat-123",
    "user_request": "Fix the authentication issue and raise a PR",
    "repository": "your-org/your-repository",
    "base_branch": "main"
  }'
```

The graph analyzes, plans, implements, reviews, and then interrupts for approval.

### Approve and resume

```bash
curl -X POST http://localhost:8000/agent/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "chat-123",
    "approved": true
  }'
```

The graph resumes, applies changes, validates, creates/pushes a branch, invokes the tool-calling LLM, executes `create_pull_request` through `ToolNode`, and returns the PR URL.

---

## 19. Exact code path for actual tool calling

The essential lines are:

```python
create_pr_tool = build_create_pull_request_tool(github_service)
tools = [create_pr_tool]

# 1. Expose schemas to the LLM.
tool_enabled_llm = llm.bind_tools(
    tools,
    parallel_tool_calls=False,
)

# 2. LLM may return AIMessage(tool_calls=[...]).
response = await tool_enabled_llm.ainvoke(messages)

# 3. Route when tool_calls exists.
if response.tool_calls:
    return "tools"

# 4. Execute the requested Python tool.
tool_node = ToolNode(tools)
```

A typical model response before execution looks like:

```python
AIMessage(
    content="",
    tool_calls=[
        {
            "name": "create_pull_request",
            "args": {
                "repository": "your-org/your-repository",
                "base_branch": "main",
                "working_branch": "ai-agent/fix-authentication-issue",
                "title": "Fix authentication issue",
                "description": "...",
            },
            "id": "call_123",
            "type": "tool_call",
        }
    ],
)
```

`ToolNode` then executes the matching function and appends a result similar to:

```python
ToolMessage(
    name="create_pull_request",
    tool_call_id="call_123",
    content='{"pr_number": 42, "pr_url": "https://github.com/.../pull/42"}',
)
```

The graph sends that `ToolMessage` back to the post-approval LLM. The LLM then returns a normal answer without another tool call, and the graph routes to `final_response`.

---

## 20. Why the tool is exposed only after approval

Do not bind destructive or side-effecting tools to every reasoning node. The graph should enforce this boundary:

```python
can_enter_tool_calling = (
    "create_pr" in state["requested_actions"]
    and state["approval_granted"]
    and state["changes_applied"]
    and state["tests_passed"]
    and state["branch_pushed"]
)
```

The LLM identifies or selects an action, but application code verifies permission and prerequisites.

---

## 21. Idempotency and retry protection

PR creation can be retried accidentally after timeouts or graph restarts. Before production use, implement these protections:

1. Store an operation key such as `chat_id:create_pull_request`.
2. Before creating a PR, query whether a PR already exists for the working branch.
3. Return the existing PR instead of creating another one.
4. Store `pr_number`, `pr_url`, branch, and commit SHA in persistent application storage.
5. Do not rely only on in-memory LangGraph state.

A possible service method:

```python
async def find_open_pull_request(
    self,
    repository: str,
    working_branch: str,
) -> PullRequestResult | None:
    ...
```

Then the tool can use:

```python
existing = await github_service.find_open_pull_request(
    repository=repository,
    working_branch=working_branch,
)

if existing:
    return {
        "pr_number": existing.number,
        "pr_url": existing.url,
        "reused_existing": True,
    }
```

---

## 22. Authentication and authorization requirements

The API example is intentionally focused on graph execution. Add production authorization before use:

1. Authenticate the FastAPI user.
2. Verify the `chat_id` belongs to that user.
3. Verify the project/repository belongs to or is accessible by that user.
4. Never accept an arbitrary local `repository_root` from the request.
5. Store GitHub credentials in a secret store.
6. Use installation tokens or short-lived credentials where possible.
7. Redact credentials from logs and traces.
8. Audit approval, commit, push, and PR operations.

Include `user_id` in configurable metadata if your checkpointer and persistence layer use it:

```python
config = {
    "configurable": {
        "thread_id": request.chat_id,
        "user_id": current_user.id,
    }
}
```

---

## 23. Production checkpointer

`MemorySaver` loses state when the process restarts and is not suitable for multiple application instances. Replace it with a persistent checkpointer compatible with your deployed LangGraph version and database.

Conceptually:

```python
checkpointer = build_persistent_checkpointer(database_url)
graph = builder.compile(checkpointer=checkpointer)
```

The same `thread_id` must be supplied when starting and resuming the graph.

---

## 24. Recommended test cases

### Intent tests

```text
"Fix authentication and raise a PR"
Expected: create_pr included

"Fix authentication but only show the diff"
Expected: create_pr excluded, apply_changes excluded

"Review authentication code"
Expected: analysis/review only
```

### Approval tests

```text
approved=false
Expected: no file write, no commit, no push, no PR

approved=true
Expected: continue to apply and validation
```

### Validation tests

```text
pytest fails
Expected: no branch push and no PR

pytest passes
Expected: continue to prepare_git
```

### Tool-calling tests

```text
No tool_calls in AIMessage
Expected: route to final_response

create_pull_request tool_call present
Expected: ToolNode executes exactly once

ToolMessage already present
Expected: action LLM summarizes result and does not call tool again
```

### Security tests

```text
relative_path="../../outside.py"
Expected: rejected

repository supplied for another user
Expected: authorization failure

second approval request after completed PR
Expected: existing operation/PR returned, no duplicate PR
```

---

## 25. Unit test for the tool-calling router

```python
from langchain_core.messages import AIMessage

from app.agent.nodes import route_after_action_llm


def test_routes_to_tools_when_model_requests_tool():
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_pull_request",
                        "args": {
                            "repository": "owner/repo",
                            "base_branch": "main",
                            "working_branch": "ai-agent/fix-auth",
                            "title": "Fix authentication",
                            "description": "Fixes authentication.",
                        },
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            )
        ]
    }

    assert route_after_action_llm(state) == "tools"


def test_routes_to_final_response_without_tool_call():
    state = {
        "messages": [AIMessage(content="No action required.")]
    }

    assert route_after_action_llm(state) == "final_response"
```

---

## 26. Tool integration test with a fake service

```python
import pytest

from app.agent.tools import build_create_pull_request_tool
from app.services.github_service import PullRequestResult


class FakeGitHubService:
    async def create_pull_request(
        self,
        repository: str,
        base_branch: str,
        working_branch: str,
        title: str,
        description: str,
    ) -> PullRequestResult:
        return PullRequestResult(
            number=42,
            url="https://example.test/pull/42",
        )


@pytest.mark.asyncio
async def test_create_pull_request_tool():
    tool = build_create_pull_request_tool(FakeGitHubService())

    result = await tool.ainvoke(
        {
            "repository": "owner/repo",
            "base_branch": "main",
            "working_branch": "ai-agent/fix-auth",
            "title": "Fix authentication",
            "description": "Fixes authentication.",
        }
    )

    assert result["pr_number"] == 42
    assert result["pr_url"] == "https://example.test/pull/42"
```

---

## 27. React interaction outline

The backend contract can remain simple:

```text
POST /agent/start
    ↓
Backend returns interrupt payload
    ↓
React displays proposed changes and pending actions
    ↓
User clicks Approve and Create PR
    ↓
POST /agent/confirm { chat_id, approved: true }
    ↓
Backend resumes the graph and eventually returns pr_url
```

Example UI labels:

```text
Approve and create PR
Reject changes
```

The approval screen should show the exact side effects:

```text
- Apply proposed changes
- Run tests
- Create a branch
- Commit and push
- Open a pull request
```

---

## 28. Architectural summary

Use each layer for a distinct responsibility:

```text
React
    Collect request and approval

FastAPI
    Authenticate, start graph, resume graph

LangGraph
    Orchestrate stages, preserve state, enforce prerequisites

LLM with bind_tools
    Return structured AIMessage.tool_calls

ToolNode
    Execute the selected tool and return ToolMessage

GitHubService
    Implement Git and GitHub API behavior

ProjectService
    Read and safely update repository files

ValidationService
    Execute application-controlled checks
```

The PR tool is genuine tool-calling because the LLM emits the structured call. However, the graph still controls when that tool-enabled LLM becomes reachable. This combines agentic selection with deterministic safety controls.
