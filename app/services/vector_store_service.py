# vector_store_service.py
from pathlib import Path
from functools import lru_cache
from langchain_chroma import Chroma

from app.core.config import settings
from app.services.embedding_service import get_embeddings


# --------------------------------------------------
# 1. VECTOR DATABASE CONFIGURATION
# --------------------------------------------------

COLLECTION_NAME = "course_copilot"


# --------------------------------------------------
# 2. GET VECTOR STORE
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_vector_store():
    settings.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(settings.VECTOR_DB_DIR),
        embedding_function=get_embeddings(),
    )

    


# --------------------------------------------------
# 3. ADD DOCUMENT CHUNKS
# --------------------------------------------------

def add_document_chunks(
    chunks: list,
    session_id: str,
    document_id: str
):

    if not session_id:
        raise ValueError("Session ID is required.")

    if not document_id:
        raise ValueError("Document ID is required.")

    if not chunks:
        raise ValueError("No chunks provided.")

    # Validate chunk ownership metadata
    for chunk in chunks:

        if chunk.metadata.get("session_id") != session_id:
            raise ValueError("Session ID mismatch in document metadata.")

        if chunk.metadata.get("document_id") != document_id:
            raise ValueError("Document ID mismatch in document metadata.")

    vector_store = get_vector_store()

    # Generate unique IDs for chunks
    chunk_ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    # Store chunks and generate embeddings
    vector_store.add_documents(
        documents=chunks,
        ids=chunk_ids
    )

    return {
        "document_id": document_id,
        "session_id": session_id,
        "total_chunks": len(chunks),
        "status": "stored"
    }


# --------------------------------------------------
# 4. SEARCH DOCUMENTS
# --------------------------------------------------

def search_documents(
    query: str,
    session_id: str,
    k: int | None = None
):

    if not session_id:
        raise ValueError("Session ID is required.")

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query=query,
        k=k or settings.RETRIEVER_TOP_K,
        filter={
            "session_id": session_id
        }
    )

    return results


# --------------------------------------------------
# 5. DELETE DOCUMENT
# --------------------------------------------------

def delete_document_chunks(
    session_id: str,
    document_id: str
):

    if not session_id or not document_id:
        raise ValueError(
            "Session ID and Document ID are required."
        )

    vector_store = get_vector_store()

    vector_store.delete(
        where={
            "$and": [
                {"session_id": session_id},
                {"document_id": document_id}
            ]
        }
    )

    return {
        "status": "deleted"
    }