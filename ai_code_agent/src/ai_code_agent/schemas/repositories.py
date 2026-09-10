from ai_code_agent.schemas import BaseModel, AfterValidator, HttpUrl, Annotated, re

GITHUB_REPO_REGEX = re.compile(
    r"^https?://(www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"
)


def validate_github_repo(url: HttpUrl) -> HttpUrl:
    """Validator to ensure the URL is a valid GitHub repository link."""
    url_str = str(url)
    match = GITHUB_REPO_REGEX.match(url_str)

    if not match:
        raise ValueError(
            "Must be a valid GitHub repository URL (e.g., 'https://github.com')"
        )

    owner, repo = match.group(2), match.group(3)

    # Block navigating into reserved GitHub sub-pages instead of real repositories
    reserved_words = {
        "settings",
        "orgs",
        "stars",
        "trending",
        "features",
        "marketplace",
    }
    if owner in reserved_words or repo in reserved_words:
        raise ValueError(
            "The provided URL points to a reserved GitHub path, not a repository."
        )

    return url


class RepositoryRequest(BaseModel):
    repo_url: Annotated[HttpUrl, AfterValidator(validate_github_repo)]


class IngestRepoResponse(BaseModel):
    message: str
    project_id: str
    repo_name: str


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # file | folder
    children: list["FileNode"] = []


class FileContentResponse(BaseModel):
    path: str
    content: str


class ProjectResponse(BaseModel):
    project_id: str
    repo_name: str
