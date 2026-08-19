import os
import aiofiles
from typing import List

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
