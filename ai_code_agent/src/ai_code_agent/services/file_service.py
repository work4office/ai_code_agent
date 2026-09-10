from pathlib import Path

from ai_code_agent.services import hashlib, List, os, aiofiles, Chroma

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "bin",
    "obj",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".cs",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".csproj",
    ".sln",
    ".html",
    ".css",
    ".sql",
}


def scan_directory(directory_path: str) -> List:
    files = []

    for root, dirs, filenames in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                files.append(os.path.join(root, filename))

    return files


def get_file_id(file_path: str) -> str:
    return hashlib.md5(file_path.encode()).hexdigest()


def get_file_fingerprint(file_path: str) -> str:
    stat = os.stat(file_path)

    value = (
        file_path,
        stat.st_size,
        stat.st_mtime_ns,
    )

    return hashlib.md5(str(value).encode()).hexdigest()


def get_existing_fingerprint(
    vectorstore: Chroma,
    file_id: str,
) -> str | None:

    result = vectorstore.get(
        ids=[file_id],
        include=["metadatas"],
    )

    metadatas = result.get("metadatas", [])

    if not metadatas:
        return None

    if not metadatas[0]:
        return None

    return metadatas[0].get("fingerprint")


async def read_file(file_path: str) -> str:
    async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return await f.read()


async def write_file(file_path: str, content: str) -> None:
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(content)


async def create_backup(file_path: str, directory_path: str) -> None:
    if os.path.exists(file_path):

        relative_path = os.path.relpath(
            file_path,
            directory_path,
        )

        backup_path = os.path.join(
            directory_path,
            ".agent_backups",
            relative_path + ".agent.backup",
        )

        os.makedirs(
            os.path.dirname(backup_path),
            exist_ok=True,
        )

        original = await read_file(file_path)
        await write_file(backup_path, original)


# This is for Deleted files which user has deleted but vector embedding still persists
def remove_deleted_files(vectorstore: Chroma, current_file_ids: set[str]):
    existing_ids = set(vectorstore.get()["ids"])
    ids_to_delete = list(existing_ids - current_file_ids)
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)


def build_tree(directory: str) -> list[dict]:
    root = Path(directory)

    def create_node(path: Path):
        if path.is_dir():
            return {
                "name": path.name,
                "path": str(path.relative_to(root)),
                "type": "folder",
                "children": [create_node(child) for child in sorted(path.iterdir())],
            }

        return {
            "name": path.name,
            "path": str(path.relative_to(root)),
            "type": "file",
        }

    return [create_node(item) for item in sorted(root.iterdir())]
