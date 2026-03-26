from crewai.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY


@tool("tavily_search")
def tavily_search(query: str) -> str:
    """Search the web using Tavily and return top 5 results with title, url, and snippet."""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=5)
        results = response.get("results", [])
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            url = r.get("url", "")
            snippet = r.get("content", r.get("snippet", "No snippet"))[:300]
            lines.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Search error: {str(e)}"
