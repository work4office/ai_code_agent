import os
import re


def get_project_name(directory_path: str) -> str:
    return os.path.basename(os.path.normpath(directory_path))


def sanitize_project_name(name: str) -> str:
    # Keep letters, numbers, underscore, dash, and dot
    return re.sub(r"[^a-zA-Z0-9_.-]", "", name)


def resolve_agent_file_path(directory_path: str, file_path: str) -> str:
    """
    Resolves file paths returned by LLM.

    Handles:
    - absolute paths
    - relative paths
    - placeholders like <project-name>.csproj
    """

    root_dir = os.path.abspath(directory_path)

    project_name = sanitize_project_name(get_project_name(root_dir))

    cleaned_path = file_path.strip()

    if not os.path.exists(cleaned_path):
        parts = cleaned_path.split("/")
        updated_parts = []
        for part in parts:
            if part.startswith("<"):
                updated_parts.append(re.sub(r"^<[^>]+>", project_name, part))
            elif part.startswith("*"):
                updated_parts.append(part.replace("*", project_name, 1))
            else:
                updated_parts.append(part)

        cleaned_path = "/".join(updated_parts)

    if os.path.isabs(cleaned_path):
        resolved_path = os.path.abspath(cleaned_path)
    else:
        resolved_path = os.path.abspath(os.path.join(root_dir, cleaned_path))

    if not resolved_path.startswith(root_dir):
        raise ValueError(f"Unsafe file path outside project directory: {resolved_path}")

    return os.path.normpath(resolved_path)
