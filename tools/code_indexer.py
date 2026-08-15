from langchain_core.documents import Document
from vectorstore.chroma_store import get_vectorstore
from tools.file_tools import read_file


def index_codebase(file_paths: list[str]) -> str:
    vectorstore = get_vectorstore()

    documents = []

    for file_path in file_paths:
        content = read_file(file_path)

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
