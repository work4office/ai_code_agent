import hashlib
import os
from langchain_chroma import Chroma
import streamlit as st
from models.llm import get_embedding, get_goggle_embedding


def get_vectorstore(collection_name: str = "codebase"):
    embeddings = get_embedding()

    directory_path = st.session_state.directory_path

    project_id = hashlib.md5(directory_path.encode()).hexdigest()

    collection_name = f"project_{project_id}"

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=os.getenv("CHROMA_DIR", "./chroma_db"),
    )
