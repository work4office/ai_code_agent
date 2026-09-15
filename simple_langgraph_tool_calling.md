# Simple LangGraph Tool Calling for Creating a Pull Request

This example contains only the genuine tool-calling part. It assumes your existing graph has already:

- analyzed and changed the code;
- received human approval;
- applied the changes;
- created and pushed a Git branch.

The tool-calling flow is:

```text
post_approval_agent
        |
        | LLM returns AIMessage(tool_calls=[...])
        v
tools (ToolNode)
        |
        | ToolMessage with PR result
        v
post_approval_agent
        |
        | LLM returns normal final message
        v
END
```

## 1. Install packages

```bash
pip install langchain langgraph langchain-openai httpx
```

## 2. Minimal complete implementation

Create one file named `pr_tool_graph.py`:

```python
import os
from typing import Annotated, TypedDict

import httpx
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


# ---------------------------------------------------------
# 1. Graph state
# ---------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# ---------------------------------------------------------
# 2. Genuine tool
# ---------------------------------------------------------

@tool
async def create_pull_request(
    repository: str,
    base_branch: str,
    working_branch: str,
    title: str,
    description: str,
) -> dict:
    """Create a GitHub pull request from an existing pushed branch."""

    url = f"https://api.github.com/repos/{repository}/pulls"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "title": title,
        "head": working_branch,
        "base": base_branch,
        "body": description,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

    data = response.json()

    return {
        "pr_number": data["number"],
        "pr_url": data["html_url"],
    }


# ---------------------------------------------------------
# 3. Bind the tool to the LLM
# ---------------------------------------------------------

tools = [create_pull_request]

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

# bind_tools allows the LLM to return AIMessage.tool_calls.
llm_with_tools = llm.bind_tools(
    tools,
    parallel_tool_calls=False,
)


# ---------------------------------------------------------
# 4. LLM node that decides whether to call the tool
# ---------------------------------------------------------

async def action_agent(state: AgentState) -> dict:
    response = await llm_with_tools.ainvoke(
        [
            SystemMessage(
                content=(
                    "You are a post-approval Git action agent. "
                    "When the user asks to create a pull request, call the "
                    "create_pull_request tool exactly once. After receiving "
                    "the tool result, return a short final response containing "
                    "the pull request information."
                )
            ),
            *state["messages"],
        ]
    )

    return {"messages": [response]}


# ---------------------------------------------------------
# 5. ToolNode executes AIMessage.tool_calls
# ---------------------------------------------------------

tool_node = ToolNode(tools)


# ---------------------------------------------------------
# 6. Build the tool-calling loop
# ---------------------------------------------------------

builder = StateGraph(AgentState)

builder.add_node("action_agent", action_agent)
builder.add_node("tools", tool_node)

builder.add_edge(START, "action_agent")

# tools_condition checks the last AIMessage:
# - tool_calls present -> "tools"
# - no tool_calls      -> END
builder.add_conditional_edges(
    "action_agent",
    tools_condition,
)

# Return ToolMessage to the LLM so it can produce a final answer.
builder.add_edge("tools", "action_agent")

graph = builder.compile()


# ---------------------------------------------------------
# 7. Run the graph after your human approval flow
# ---------------------------------------------------------

async def create_pr_after_approval() -> dict:
    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Create the pull request using these exact values:\n"
                        "repository: my-org/my-repository\n"
                        "base_branch: main\n"
                        "working_branch: ai-agent/fix-authentication\n"
                        "title: Fix authentication issue\n"
                        "description: Fixes the authentication issue and "
                        "adds the related tests."
                    )
                )
            ]
        }
    )

    return result
```

## 3. Call it from your existing post-approval node

Once your current workflow has received approval and pushed the branch, invoke this small graph:

```python
pr_result = await graph.ainvoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "Create the pull request using these exact values:\n"
                    f"repository: {state['repository']}\n"
                    f"base_branch: {state['base_branch']}\n"
                    f"working_branch: {state['working_branch']}\n"
                    f"title: {state['pr_title']}\n"
                    f"description: {state['pr_description']}"
                )
            )
        ]
    }
)
```

To read the final response:

```python
final_message = pr_result["messages"][-1]
print(final_message.content)
```

## 4. What makes this genuine tool-calling?

The important line is:

```python
llm_with_tools = llm.bind_tools(tools)
```

The LLM receives the tool schema and can respond with a structured call similar to:

```python
AIMessage(
    content="",
    tool_calls=[
        {
            "name": "create_pull_request",
            "args": {
                "repository": "my-org/my-repository",
                "base_branch": "main",
                "working_branch": "ai-agent/fix-authentication",
                "title": "Fix authentication issue",
                "description": "Fixes authentication and adds tests.",
            },
            "id": "call_123",
            "type": "tool_call",
        }
    ],
)
```

The LLM does not execute Python itself. `ToolNode` reads that structured request and calls `create_pull_request`:

```python
tool_node = ToolNode(tools)
```

After execution, `ToolNode` adds a `ToolMessage` containing the function result. The edge below sends that result back to the LLM:

```python
builder.add_edge("tools", "action_agent")
```

The LLM then returns a normal final message, without `tool_calls`, and `tools_condition` ends the graph.

## 5. How to inspect the tool call while learning

Temporarily print the response inside `action_agent`:

```python
async def action_agent(state: AgentState) -> dict:
    response = await llm_with_tools.ainvoke(
        [
            SystemMessage(
                content=(
                    "When asked to create a PR, call create_pull_request."
                )
            ),
            *state["messages"],
        ]
    )

    print("Tool calls:", response.tool_calls)

    return {"messages": [response]}
```

Before execution, you should see a value similar to:

```python
[
    {
        "name": "create_pull_request",
        "args": {...},
        "id": "call_123",
        "type": "tool_call",
    }
]
```

On the second pass, after the tool result is returned, `response.tool_calls` should normally be empty.

## 6. Environment variables

Set both tokens before running:

```env
OPENAI_API_KEY=your-openai-key
GITHUB_TOKEN=your-github-token
```

Do not place either token directly in source code.

## 7. Optional local test without creating a real PR

While learning, replace the real tool body with a fake result:

```python
@tool
async def create_pull_request(
    repository: str,
    base_branch: str,
    working_branch: str,
    title: str,
    description: str,
) -> dict:
    """Create a GitHub pull request from an existing pushed branch."""

    print(
        "Tool executed:",
        repository,
        base_branch,
        working_branch,
        title,
    )

    return {
        "pr_number": 101,
        "pr_url": "https://example.test/pull/101",
    }
```

This verifies the full genuine tool-calling loop without calling GitHub:

```text
LLM -> AIMessage.tool_calls -> ToolNode -> Python tool
    -> ToolMessage -> LLM final answer
```

## 8. Keep the first version intentionally simple

For your first implementation:

- keep only one tool;
- call this graph only after human approval;
- pass already verified PR arguments;
- let your existing code handle branch creation and push;
- add retries, idempotency, service classes, and persistent state later.

The four essential pieces are:

```python
@tool
async def create_pull_request(...):
    ...

llm_with_tools = llm.bind_tools([create_pull_request])

tool_node = ToolNode([create_pull_request])

builder.add_conditional_edges("action_agent", tools_condition)
builder.add_edge("tools", "action_agent")
```
