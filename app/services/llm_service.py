from functools import lru_cache
from langchain_groq import ChatGroq

from app.core.config import settings


@lru_cache(maxsize=1)
def get_llm():
    settings.validate_groq_api_key()

    return ChatGroq(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.GROQ_API_KEY,
        reasoning_effort="medium",
        timeout=30,
        max_retries=1,
    )