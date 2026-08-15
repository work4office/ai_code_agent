from vectorstore.chroma_store import get_vectorstore


def retrieve_relevant_code(user_request: str, k: int = 8) -> dict:
    vectorstore = get_vectorstore()

    context_parts = []

    relevant_docs = vectorstore.similarity_search(user_request, k=k)

    for doc in relevant_docs:
        file_path = doc.metadata.get("file_path", "unknown")
        content = doc.page_content

        context_parts.append(f"\n\n--- FILE: {file_path} ---\n{content}")

    return {"retrieved_documents": "\n".join(context_parts)}
