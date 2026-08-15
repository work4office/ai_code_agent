import difflib
from typing import Any

from agent.schemas import GeneratedChanges, ReviewResult

def generate_diff(file_path: str, old_content: str, new_content: str):

    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=file_path,
        tofile=f"{file_path}.updated",
        lineterm="",
    )

    return "\n".join(diff)


def coerce_review_result(value: Any) -> ReviewResult:
    if isinstance(value, ReviewResult):
        return value

    if isinstance(value, dict):
        return ReviewResult(**value)

    raise TypeError("The reviewer did not return a structured ReviewResult.")


def coerce_generated_change(value: Any) -> GeneratedChanges:
    if isinstance(value, GeneratedChanges):
        return value

    return GeneratedChanges.model_validate(value)
