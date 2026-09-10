from ai_code_agent.services import hashlib, subprocess, os, Path


class GitService:

    async def clone_or_pull(
        self,
        repo_url: str,
        local_path: str,
    ) -> None:

        path = Path(local_path)

        if path.exists():

            subprocess.run(
                ["git", "pull", "origin", "HEAD"],
                cwd=local_path,
                check=True,
            )

        else:

            subprocess.run(
                [
                    "git",
                    "clone",
                    repo_url,
                    local_path,
                ],
                check=True,
            )

    async def get_commit_hash(
        self,
        repo_path: str,
    ) -> str:
        """return SHA-1 commit hash of the current HEAD"""
        return (
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "HEAD",
                ],
                cwd=repo_path,
            )
            .decode()
            .strip()
        )

    def get_repo_name(
        self,
        repo_url: str,
    ) -> str:

        return repo_url.rstrip("/").split("/")[-1].replace(".git", "")

    def generate_project_id(self, repo_url: str) -> str:
        return hashlib.sha256(repo_url.lower().strip().encode()).hexdigest()

    def get_collection_name(self, project_id: str) -> str:
        return f"repo_{project_id}"

    def get_repo_dir(self, project_id: str) -> str:
        return os.path.join("./repos", project_id)
