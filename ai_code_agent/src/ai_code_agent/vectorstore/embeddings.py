from ai_code_agent.vectorstore import os, Chroma, get_goggle_embedding


def get_vectorstore(collection_name: str):
    embeddings = get_goggle_embedding()

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=os.getenv("CHROMA_DIR", "./chroma_db"),
    )
