from ai_code_agent.services import (
    ReviewResult,
    ImplementationPlan,
    RunnableConfig,
    AgentState,
    Command,
    Path,
    Any,
    Request,
)


class GraphService:

    async def invoke_graph(
        self,
        path: str,
        user_request: str,
        collection_name: str,
        thread_id: str,
        request: Request,
    ) -> dict[str, Any] | Any:
        graph = request.app.state.graph
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        initial_state: AgentState = {
            "directory_path": path,
            "user_request": user_request,
            "collection_name": collection_name,
            "project_files": [],
            "retrieved_context": "",
            "retrieved_files": {},
            "analysis": "",
            "implementation_plan": ImplementationPlan(),
            "generated_changes": {},
            "review_result": ReviewResult(),
            "approved": False,
            "applied_files": [],
            "test_result": "",
            "retry_count": 0,
            "final_summary": "",
        }

        return await graph.ainvoke(initial_state, config=config)

    def get_confirmation_changes(self, path: str, result: dict[str, Any] | Any):
        changes = []
        if "__interrupt__" in result:
            payload = result["__interrupt__"][0].value
            for index, (file_path, diff) in enumerate(payload["diffs"].items()):
                old_code = diff["original_content"]
                updated_code = diff["new_content"]
                repo_root = Path(path).absolute()
                relative_path = Path(file_path).relative_to(repo_root)
                changes.append(
                    {
                        "id": index,
                        "old_code": old_code,
                        "updated_code": updated_code,
                        "file_path": str(relative_path),
                    }
                )
        return changes

    async def confirm_changes(
        self, request: Request, thread_id: str, is_confirmed: bool
    ):
        graph = request.app.state.graph
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        return await graph.ainvoke(Command(resume=is_confirmed), config=config)
