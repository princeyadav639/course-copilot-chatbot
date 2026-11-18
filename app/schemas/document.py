# schemas/document.py
from typing import Literal

from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    """
    Information about an uploaded PDF document.
    """

    document_id: str

    filename: str

    total_chunks: int = Field(
        ge=0,
        description="Number of text chunks created from the PDF"
    )


class DocumentUploadResponse(BaseModel):
    """
    Response returned after successfully uploading a PDF.
    """

    document_id: str

    filename: str

    total_chunks: int = Field(ge=0)

    status: Literal["success"] = "success"


class DocumentDeleteResponse(BaseModel):
    """
    Response returned after deleting a PDF document.
    """

    document_id: str

    status: Literal["deleted"] = "deleted"


class DocumentListResponse(BaseModel):
    """
    Response containing the user's uploaded documents.
    """

    documents: list[DocumentInfo] = Field(
        default_factory=list
    )

    total_documents: int = Field(
        ge=0,
        description="Total number of uploaded documents"
    )