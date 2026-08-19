import difflib
from typing import Any, LiteralString

from agent.schemas import GeneratedChanges, ReviewResult
from tools.file_tools import read_file


async def generate_diff(file_path: str, change: GeneratedChanges):
    if change.action == "modify":
        original_content = await read_file(file_path)
    else:
        original_content = ""
    new_content = change.updated_content
    diff = difflib.unified_diff(
        original_content.splitlines(),
        new_content.splitlines(),
        fromfile=file_path,
        tofile=f"{file_path}.updated",
        lineterm="",
    )

    return "\n".join(diff)


async def get_generated_diffs(generated_changes: dict[str, GeneratedChanges]):
    generated_diffs: dict[str, dict] = {}
    for file_path, change in generated_changes.items():
        if change.action == "modify":
            original_content = await read_file(file_path)
        else:
            original_content = ""
        new_content = change.updated_content
        generated_diffs[file_path] = {
            "original_content": original_content,
            "new_content": new_content,
        }
    return generated_diffs


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


async def generate_review_context(
    generated_changes: dict[str, GeneratedChanges],
) -> LiteralString:

    review_context_parts = []

    for file_path, change in generated_changes.items():

        if change.action == "modify":
            diff = await generate_diff(file_path, change)

            if diff:
                review_context_parts.append(f"""
                FILE: {file_path}
                CHANGE TYPE: MODIFY
                DIFF: {diff}
                """)

        else:

            if len(change.updated_content) < 3000:
                review_context_parts.append(f"""
                FILE: {file_path}
                CHANGE TYPE: CREATE
                CONTENT: {change.updated_content}
                """)
            elif len(change.updated_content) < 10000:
                review_context_parts.append(f"""
                FILE: {file_path}
                CHANGE TYPE: CREATE
                CONTENT: {change.updated_content[:4000]}
                """)
            else:
                review_context_parts.append(f"""
                FILE: {file_path}
                CHANGE TYPE: CREATE
                SUMMARY: {change.summary}
                """)
    review_context = "\n\n".join(review_context_parts)
    return review_context
