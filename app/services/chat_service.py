# chat_service.py
from langchain_core.messages import HumanMessage, AIMessage

from app.core.config import settings

from app.services.chat_history_service import (
    trim_history,
    estimate_message_tokens
)

from app.services.agent_service import run_agent


# --------------------------------------------------
# 1. CONVERT CONTENT INTO TEXT
# --------------------------------------------------

def content_to_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if isinstance(text, str):
                    parts.append(text)

            else:

                text = getattr(item, "text", None)

                if isinstance(text, str):
                    parts.append(text)

        return "\n".join(parts)

    return str(content) if content is not None else ""


# --------------------------------------------------
# 2. CONVERT HISTORY INTO LANGCHAIN MESSAGES
# --------------------------------------------------

def convert_history_to_messages(history: list) -> list:

    messages = []

    for message in history:

        if not isinstance(message, dict):
            continue

        role = message.get("role")

        content = content_to_text(
            message.get("content", "")
        )

        if not content.strip():
            continue

        if role == "user":

            messages.append(
                HumanMessage(content=content)
            )

        elif role == "assistant":

            messages.append(
                AIMessage(content=content)
            )

    return messages


# --------------------------------------------------
# 3. GENERATE CHAT RESPONSE
# --------------------------------------------------

def generate_chat_response(
    query: str,
    session_id: str,
    history: list | None = None
) -> dict:

    # Step 1: Validate user query

    if not query or not query.strip():
        raise ValueError("Message cannot be empty.")

    if not session_id:
        raise ValueError("Session ID is required.")

    if history is None:
        history = []

    # Step 2: Calculate available history budget

    total_budget = settings.HISTORY_TOKEN_BUDGET

    current_message = {
        "role": "user",
        "content": query
    }

    current_message_tokens = estimate_message_tokens(
        current_message
    )

    history_budget = max(
        0,
        total_budget - current_message_tokens
    )

    # Step 3: Trim conversation history

    trimmed_history = trim_history(
        history=history,
        token_budget=history_budget,
        max_messages=settings.MAX_HISTORY_MESSAGES
    )

    # Step 4: Convert history into LangChain messages

    chat_history = convert_history_to_messages(
        trimmed_history
    )

    # Step 5: Execute AI agent

    agent_result = run_agent(
        query=query,
        session_id=session_id,
        chat_history=chat_history
    )

    # Step 6: Extract response
    print("DEBUG 10: Extracting response content", flush=True)

    answer = content_to_text(
        agent_result.get("answer", "")
    )

    # Step 7: Return final response

    return {
        "answer": answer,
        "sources": agent_result.get("sources", []),
        "total_chunks": agent_result.get("total_chunks", 0),
        "history_messages_used": len(trimmed_history)
    }
print("DEBUG 13: Chat service returning response", flush=True)