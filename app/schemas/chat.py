# schemas/chat.py
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Schema for incoming chatbot requests.
    """

    message: str = Field(
        min_length=1,
        max_length=8000,
        description="User's message"
    )

    history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """
    Schema for chatbot responses.
    """

    answer: str

    sources: list[dict[str, Any]] = Field(
        default_factory=list
    )

    total_chunks: int = 0

    history_messages_used: int = 0