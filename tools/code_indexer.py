from langchain_core.documents import Document
from vectorstore.chroma_store import get_vectorstore
from tools.file_tools import read_file


async def index_codebase(file_paths: list[str], directory_path: str) -> str:
    vectorstore = get_vectorstore(directory_path)

    documents = []

    for file_path in file_paths:
        content = await read_file(file_path)

        if not content.strip():
            continue

        doc = Document(
            page_content=content,
            metadata={"file_path": file_path, "file_name": file_path.split("/")[-1]},
        )

        documents.append(doc)

    ids = [f"file_{i}" for i in range(len(documents))]

    if documents:
        vectorstore.add_documents(documents=documents, ids=ids)

    return f"Indexed {len(documents)} files"
