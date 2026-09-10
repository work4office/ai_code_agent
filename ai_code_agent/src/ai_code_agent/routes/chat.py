from ai_code_agent.routes import (
    APIRouter,
    status,
    SessionDep,
    Users,
    GitService,
    RepositoryService,
    GraphService,
    get_current_user,
    Depends,
    Annotated,
    ChatResponse,
    ChatRequest,
    ChatConfirmResponse,
    Request,
    Repositories,
    ChatConfirmRequest,
)

router = APIRouter(prefix="/chat")


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def start_chat(
    chat_info: ChatRequest,
    request: Request,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    repository_service = RepositoryService(session)
    gitService = GitService()
    graphService = GraphService()

    id = current_user.id if current_user.id is not None else 0
    repos: Repositories | None = await repository_service.get_by_project_id(
        user_id=id, project_id=chat_info.project_id
    )

    path = gitService.get_repo_dir(chat_info.project_id)

    collection_name = repos.collection_name if repos is not None else ""

    stateResult = await graphService.invoke_graph(
        user_request=chat_info.user_request,
        path=path,
        collection_name=collection_name,
        thread_id=chat_info.project_id,
        request=request,
    )
    changes = graphService.get_confirmation_changes(path=path, result=stateResult)
    return {"changes": changes, "message": "Review new changes"}


@router.post(
    "/confirm",
    response_model=ChatConfirmResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_user(
    info: ChatConfirmRequest,
    request: Request,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    graphService = GraphService()

    result = await graphService.confirm_changes(
        request=request,
        thread_id=info.project_id,
        is_confirmed=info.is_confirmed,
    )
    return {
        "status": "completed",
        "approved": result["approved"],
        "applied_files": result["applied_files"],
    }
