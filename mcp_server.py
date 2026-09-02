import os
import json
from tavily import TavilyClient
from fastmcp import FastMCP

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the MCP server."}]
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

def format_results(results: list) -> str:
    cleaned = []
    for item in results:
        cleaned.append({
            "title": str(item.get("title", "")).strip(),
            "url": str(item.get("url", "")).strip(),
            "content": str(item.get("content", "")).strip()
        })
    return json.dumps(cleaned, ensure_ascii=False)

@mcp.tool
def search_products(query: str) -> str:
    results = search_web(
        f"best {query} specific product models specifications India 2026",
        5
    )
    return format_results(results)

@mcp.tool
def search_prices(query: str) -> str:
    results = search_web(
        f"{query} current price India Amazon Flipkart Croma Reliance Digital official store 2026",
        5
    )
    return format_results(results)

@mcp.tool
def search_reviews(query: str) -> str:
    results = search_web(
        f"{query} product reviews customer reviews pros cons India 2026",
        5
    )
    return format_results(results)

@mcp.tool
def search_comparison(query: str) -> str:
    results = search_web(
        f"{query} best alternatives comparison India 2026 specific models",
        5
    )
    return format_results(results)

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
