from ai_code_agent.services import (
    UTC,
    datetime,
    Repositories,
    scan_directory,
    GitService,
    RepositoryService,
)
from ai_code_agent.vectorstore.indexer import index_codebase


class IndexingService:

    def __init__(
        self,
        repository_service: RepositoryService,
        git_service: GitService,
    ):
        self.repository_service = repository_service
        self.git_service = git_service

    async def index_github_repo(
        self,
        user_id: int,
        repo_url: str,
    ):
        project_id = self.git_service.generate_project_id(repo_url)

        repo_dir = self.git_service.get_repo_dir(project_id)

        collection_name = self.git_service.get_collection_name(project_id)

        repo_name = self.git_service.get_repo_name(repo_url)

        await self.git_service.clone_or_pull(
            repo_url,
            repo_dir,
        )
        latest_commit = await self.git_service.get_commit_hash(
            repo_dir,
        )
        existing_repo = await self.repository_service.get_by_project_id(
            user_id=user_id,
            project_id=project_id,
        )

        if existing_repo and existing_repo.commit_hash == latest_commit:
            return {
                "message": "Repository already indexed",
                "project_id": project_id,
                "repo_name": repo_name,
            }

        file_paths = scan_directory(repo_dir)

        result = await index_codebase(
            file_paths=file_paths,
            collection_name=collection_name,
        )

        if existing_repo:

            existing_repo.commit_hash = latest_commit

            await self.repository_service.update_commit_hash(
                user_id=user_id, project_id=project_id, commit_hash=latest_commit
            )

        else:
            new_repo = Repositories(
                user_id=user_id,
                project_id=project_id,
                repo_name=repo_name,
                repo_url=repo_url,
                commit_hash=latest_commit,
                collection_name=collection_name,
            )

            await self.repository_service.create(repo=new_repo)

        return {"message": result, "project_id": project_id, "repo_name": repo_name}
