# document_service.py
from pathlib import Path

from app.utils.pdf_processor import process_pdf

from app.services.vector_store_service import (
    add_document_chunks,
    delete_document_chunks
)


# --------------------------------------------------
# 1. INGEST DOCUMENT
# --------------------------------------------------

def ingest_document(
    file_path: Path,
    original_filename: str,
    document_id: str,
    session_id: str
):

    # Step 1: Process PDF and create chunks
    chunks = process_pdf(
        file_path=file_path,
        original_filename=original_filename,
        document_id=document_id,
        session_id=session_id
    )

    # Step 2: Store chunks in ChromaDB
    result = add_document_chunks(
        chunks=chunks,
        session_id=session_id,
        document_id=document_id
    )

    # Step 3: Return ingestion details
    return {"document_id":document_id,
        "filename": original_filename,
        "total_chunks": result["total_chunks"],
        "status": "success"
    }


# --------------------------------------------------
# 2. DELETE DOCUMENT
# --------------------------------------------------

def remove_document(
    session_id: str,
    document_id: str
):

    result = delete_document_chunks(
        session_id=session_id,
        document_id=document_id
    )

    return {
        "document_id": document_id,
        "status": result["status"]
    }