from ai_code_agent.services import Repositories, select
from ai_code_agent.database.session import SessionDep


class RepositoryService:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_by_project_id(
        self,
        user_id: int,
        project_id: str,
    ) -> Repositories | None:

        stmt = select(Repositories).where(
            Repositories.project_id == project_id, Repositories.user_id == user_id
        )

        result = self.session.exec(stmt)

        return result.one_or_none()

    async def create(self, repo: Repositories) -> Repositories:

        self.session.add(repo)
        self.session.commit()
        self.session.refresh(repo)

        return repo

    async def get_project_list(self, user_id: int) -> list[tuple[str, str]]:
        stmt = select(Repositories.project_id, Repositories.repo_name).where(
            Repositories.user_id == user_id
        )

        result = self.session.exec(stmt)

        return list(result.all())

    async def update_commit_hash(
        self,
        user_id: int,
        project_id: str,
        commit_hash: str,
    ) -> None:

        repo = await self.get_by_project_id(user_id, project_id)

        if not repo:
            return

        repo.commit_hash = commit_hash

        self.session.commit()
