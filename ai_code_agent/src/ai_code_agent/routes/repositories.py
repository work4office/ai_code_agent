from ai_code_agent.routes import (
    APIRouter,
    status,
    SessionDep,
    Users,
    IndexingService,
    GitService,
    RepositoryService,
    RepositoryRequest,
    get_current_user,
    Depends,
    Annotated,
    FileNode,
    IngestRepoResponse,
    build_tree,
    aiofiles,
    os,
    FileContentResponse,
    ProjectResponse,
)

router = APIRouter(prefix="/repositories")


@router.post(
    "",
    response_model=IngestRepoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_repo(
    repository: RepositoryRequest,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    repository_service = RepositoryService(session)

    indexing_service = IndexingService(
        repository_service=repository_service,
        git_service=GitService(),
    )
    id = current_user.id if current_user.id is not None else 0
    return await indexing_service.index_github_repo(
        user_id=id,
        repo_url=str(repository.repo_url),
    )


@router.get(
    "/projects", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK
)
async def get_projects(
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    repository_service = RepositoryService(session)
    id = current_user.id if current_user.id is not None else 0
    return await repository_service.get_project_list(id)


@router.get(
    "/{project_id}/tree", response_model=list[FileNode], status_code=status.HTTP_200_OK
)
async def get_file_tree(
    project_id: str,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    git_service = GitService()
    repo_dir = git_service.get_repo_dir(project_id)

    tree = build_tree(repo_dir)

    return tree


@router.get(
    "/{project_id}/file",
    response_model=FileContentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_file_content(
    project_id: str,
    path: str,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    git_service = GitService()
    repo_dir = git_service.get_repo_dir(project_id)

    file_path = os.path.join(
        repo_dir,
        path,
    )

    async with aiofiles.open(file_path, encoding="utf-8") as file:
        content = await file.read()

    return {
        "path": path,
        "content": content,
    }
