import os
import subprocess


def detect_test_command(directory_path: str) -> str | None:
    files = os.listdir(directory_path)

    if "package.json" in files:
        return "npm test"

    if "pytest.ini" in files or "pyproject.toml" in files:
        return "pytest"

    if any(f.endswith(".sln") for f in files):
        return "dotnet test"

    return None


def run_tests(directory_path: str) -> str:
    command = detect_test_command(directory_path)

    if not command:
        return "No test command detected."

    result = subprocess.run(
        command, cwd=directory_path, shell=True, capture_output=True, text=True
    )

    return result.stdout + "\n" + result.stderr
