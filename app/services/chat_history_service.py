# chat_history_service.py
from typing import Any

from app.core.config import settings


# --------------------------------------------------
# 1. EXTRACT TEXT FROM MESSAGE CONTENT
# --------------------------------------------------

def extract_message_text(content: Any) -> str:
    """
    Extract readable text from message content.
    Supports both plain strings and content blocks.
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

        return " ".join(text_parts)

    return str(content) if content is not None else ""


# --------------------------------------------------
# 2. ESTIMATE MESSAGE TOKENS
# --------------------------------------------------

def estimate_message_tokens(message: dict) -> int:
    """
    Estimate tokens using text length.

    This is an approximation, not an exact tokenizer.
    """

    content = extract_message_text(message.get("content", ""))

    # Rough estimate: 1 token ≈ 4 characters.
    text_tokens = (len(content) + 3) // 4

    # Additional tokens for role and message formatting.
    formatting_tokens = 8

    return text_tokens + formatting_tokens


# --------------------------------------------------
# 3. TRIM CONVERSATION HISTORY
# --------------------------------------------------

def trim_history(
    history: list,
    token_budget: int | None = None,
    max_messages: int | None = None
) -> list:
    """
    Keep the most recent messages within token and
    message limits.
    """

    if not history:
        return []

    if token_budget is None:
        token_budget = settings.HISTORY_TOKEN_BUDGET

    if max_messages is None:
        max_messages = settings.MAX_HISTORY_MESSAGES

    if token_budget <= 0:
        raise ValueError("Token budget must be greater than zero.")

    if max_messages <= 0:
        raise ValueError("Maximum messages must be greater than zero.")

    selected_messages = []
    used_tokens = 0

    # Start from the newest message.
    for message in reversed(history):

        if not isinstance(message, dict):
            continue

        role = message.get("role")

        # Only keep normal conversation messages.
        if role not in ("user", "assistant"):
            continue

        content = extract_message_text(message.get("content", ""))

        if not content.strip():
            continue

        normalized_message = {
            "role": role,
            "content": content
        }

        message_tokens = estimate_message_tokens(
            normalized_message
        )

        # Stop if either limit would be exceeded.
        if len(selected_messages) >= max_messages:
            break

        if used_tokens + message_tokens > token_budget:
            break

        selected_messages.append(normalized_message)
        used_tokens += message_tokens

    # Restore chronological order.
    selected_messages.reverse()

    return selected_messages


# --------------------------------------------------
# 4. GET HISTORY STATISTICS
# --------------------------------------------------

def get_history_stats(history: list) -> dict:
    """
    Return useful information about trimmed history.
    """

    total_tokens = sum(
        estimate_message_tokens(message)
        for message in history
    )

    return {
        "total_messages": len(history),
        "estimated_tokens": total_tokens
    }