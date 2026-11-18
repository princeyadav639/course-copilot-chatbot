# tools/wikipedia_search.py
import requests


# --------------------------------------------------
# 1. WIKIPEDIA SEARCH
# --------------------------------------------------

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def search_wikipedia(
    query: str,
    max_results: int = 3
) -> list:
    """
    Search Wikipedia and return article summaries.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 5:
        raise ValueError("max_results must be between 1 and 5.")

    try:
        # Step 1: Search for Wikipedia articles

        search_response = requests.get(
            WIKIPEDIA_API_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query.strip(),
                "srlimit": max_results,
                "format": "json"
            },
            headers={
                "User-Agent": "CourseCopilot/1.0 (educational project)"
            },
            timeout=10
        )

        search_response.raise_for_status()

        search_data = search_response.json()

        search_results = search_data.get(
            "query", {}
        ).get("search", [])

        formatted_results = []

        # Step 2: Get summary of each article

        for result in search_results:

            page_id = result.get("pageid")

            if not page_id:
                continue

            summary_response = requests.get(
                WIKIPEDIA_API_URL,
                params={
                    "action": "query",
                    "pageids": page_id,
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "format": "json"
                },
                headers={
                    "User-Agent": "CourseCopilot/1.0 (educational project)"
                },
                timeout=10
            )

            summary_response.raise_for_status()

            summary_data = summary_response.json()

            pages = summary_data.get(
                "query", {}
            ).get("pages", {})

            page = pages.get(str(page_id), {})

            formatted_results.append({
                "title": page.get("title", ""),
                "url": (
                    "https://en.wikipedia.org/?curid="
                    + str(page_id)
                ),
                "summary": page.get("extract", "")
            })

        return formatted_results

    except requests.RequestException as error:
        raise RuntimeError(
            "Wikipedia search failed. Please try again later."
        ) from error

    except ValueError as error:
        if "Search query" in str(error) or "max_results" in str(error):
            raise
        raise RuntimeError(
            "Wikipedia returned an invalid response."
        ) from error