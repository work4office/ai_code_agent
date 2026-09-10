from ai_code_agent.services.file_service import (
    get_file_id,
    get_existing_fingerprint,
    get_file_fingerprint,
    read_file,
    remove_deleted_files,
)
from ai_code_agent.vectorstore import (
    os,
    get_vectorstore,
    Document,
)

# ====================== FUTURE IMPLEMENTATION ==================================
# Re-index after apply_changes_node() because that's where files actually change
#  -- this can be implemented after Auth implementatin with below flow
# Load project
# ↓
# Index once
# ↓
# Explain AuthController
# ↓
# Create JWT
# ↓
# Login
# ↓
# Add Unit Tests


async def index_codebase(file_paths: list[str], collection_name: str) -> str:

    vectorstore = get_vectorstore(collection_name)

    added = 0
    updated = 0
    skipped = 0

    current_file_ids: set[str] = set()
    for file_path in file_paths:

        file_id = get_file_id(file_path)
        current_file_ids.add(file_id)

        fingerprint = get_file_fingerprint(file_path)

        existing_fingerprint = get_existing_fingerprint(
            vectorstore,
            file_id,
        )

        # Validate file change
        if existing_fingerprint == fingerprint:
            skipped += 1
            continue

        content = await read_file(file_path)

        if not content.strip():
            continue

        document = Document(
            page_content=content,
            metadata={
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "fingerprint": fingerprint,
            },
        )

        # Existing file changed
        if existing_fingerprint:

            vectorstore.delete(ids=[file_id])

            updated += 1

        # New file
        else:
            added += 1
        if document:
            vectorstore.add_documents(
                [document],
                ids=[file_id],
            )
    remove_deleted_files(vectorstore, current_file_ids)

    return f"Added={added}, " f"Updated={updated}, " f"Skipped={skipped}"
