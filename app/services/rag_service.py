# rag_service.py
from app.services.vector_store_service import search_documents


# --------------------------------------------------
# 1. RETRIEVE RELEVANT DOCUMENTS
# --------------------------------------------------

def retrieve_context(
    query: str,
    session_id: str,
    k: int | None = None
) -> list:
    """
    Search ChromaDB for document chunks relevant
    to the user's question.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not session_id:
        raise ValueError("Session ID is required.")

    documents = search_documents(
        query=query,
        session_id=session_id,
        k=k
    )

    return documents


# --------------------------------------------------
# 2. FORMAT RETRIEVED DOCUMENTS
# --------------------------------------------------

def format_context(documents: list) -> str:
    """
    Convert retrieved document chunks into
    readable context for the LLM.
    """

    if not documents:
        return "No relevant information was found in the uploaded documents."

    context_parts = []

    for index, document in enumerate(documents, start=1):

        content = document.page_content.strip()

        if not content:
            continue

        metadata = document.metadata

        source_file = metadata.get(
            "source_file",
            "Unknown document"
        )

        page_number = metadata.get(
            "page_number",
            "Unknown"
        )

        formatted_chunk = (
            f"[Document {index}]\n"
            f"Source: {source_file}\n"
            f"Page: {page_number}\n"
            f"Content:\n{content}"
        )

        context_parts.append(formatted_chunk)

    if not context_parts:
        return "No readable information was found in the retrieved documents."

    return "\n\n".join(context_parts)


# --------------------------------------------------
# 3. COMPLETE RETRIEVAL PIPELINE
# --------------------------------------------------

def get_relevant_context(
    query: str,
    session_id: str,
    k: int | None = None
) -> dict:
    """
    Retrieve relevant chunks and return formatted
    context along with source information.
    """

    documents = retrieve_context(
        query=query,
        session_id=session_id,
        k=k
    )

    context = format_context(documents)

    sources = []

    for document in documents:

        metadata = document.metadata

        source = {
            "filename": metadata.get(
                "source_file",
                "Unknown document"
            ),
            "page_number": metadata.get(
                "page_number",
                "Unknown"
            )
        }

        if source not in sources:
            sources.append(source)

    return {
        "context": context,
        "sources": sources,
        "total_documents": len(documents)
    }