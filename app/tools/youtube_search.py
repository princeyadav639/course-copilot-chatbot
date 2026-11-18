# tools/youtube_search.py
from langchain_community.tools import YouTubeSearchTool

youtube_search = YouTubeSearchTool()

def search_youtube(
    query: str,
    max_results: int = 5
) -> str:
    """
    Search YouTube and return relevant video details.
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    try:
        youtube_tool = YouTubeSearchTool()

        results = youtube_tool.run(
            f"{query.strip()}, {max_results}"
        )

        return results

    except Exception as error:
        raise RuntimeError(
            "YouTube search failed. Please try again later."
        ) from error