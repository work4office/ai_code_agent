import os
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


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
