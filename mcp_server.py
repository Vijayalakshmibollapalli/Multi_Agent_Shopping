import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5):
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the remote MCP server."}]

    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False
        )

        return result.get("results", [])

    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]


def clean_results(results):
    cleaned = []

    for item in results:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        content = str(item.get("content", "")).strip()

        if title or url or content:
            cleaned.append({
                "title": title,
                "url": url,
                "content": content
            })

    return cleaned


def compact_results(results, limit=5000):
    cleaned = clean_results(results)
    return json.dumps(cleaned, ensure_ascii=False)[:limit]


@mcp.tool
def search_products(query: str) -> str:
    search_query = f"{query} India best products exact models specifications 2026"
    results = search_web(search_query, 5)
    return compact_results(results, 5000)


@mcp.tool
def search_prices(query: str) -> str:
    search_query = f"{query} India current price exact product model Amazon Flipkart Croma official price 2026"
    results = search_web(search_query, 5)
    return compact_results(results, 5000)


@mcp.tool
def search_reviews(query: str) -> str:
    search_query = f"{query} India product reviews pros cons customer experience 2026"
    results = search_web(search_query, 5)
    return compact_results(results, 4500)


@mcp.tool
def search_comparison(query: str) -> str:
    search_query = f"{query} India product comparison alternatives exact models 2026"
    results = search_web(search_query, 5)
    return compact_results(results, 4500)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
