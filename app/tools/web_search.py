# tools/web_search.py
from ddgs import DDGS


# --------------------------------------------------
# 1. WEB SEARCH
# --------------------------------------------------

def search_web(
    query: str,
    max_results: int = 5
) -> list:
    """
    Search the web using DuckDuckGo.

    Returns a list of search results containing
    title, URL, and snippet.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    try:
        search_results = DDGS().text(
            query.strip(),
            max_results=max_results
        )

        formatted_results = []

        for result in search_results:

            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        return formatted_results

    except Exception as error:
        raise RuntimeError(
            "Web search failed. Please try again later."
        ) from error