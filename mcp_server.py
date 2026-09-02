import os
import json
from tavily import TavilyClient
from fastmcp import FastMCP

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "TAVILY_ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the remote MCP server."}]
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=True)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]

def compact_results(results: list, limit: int = 5000) -> str:
    clean = []
    for item in results:
        clean.append({"title": str(item.get("title", "")).strip(), "url": str(item.get("url", "")).strip(), "content": str(item.get("content", "")).strip()})
    return json.dumps(clean, ensure_ascii=False)[:limit]

@mcp.tool
def search_products(query: str) -> str:
    return compact_results(search_web(f"{query} best products models specifications India 2026", 5), 5000)

@mcp.tool
def search_prices(query: str) -> str:
    return compact_results(search_web(f"{query} current price India official Amazon Flipkart Croma Reliance Digital 2026", 5), 5000)

@mcp.tool
def search_reviews(query: str) -> str:
    return compact_results(search_web(f"{query} reviews customer feedback pros cons India 2026", 5), 5000)

@mcp.tool
def search_comparison(query: str) -> str:
    return compact_results(search_web(f"{query} comparison alternatives competitors India 2026", 5), 5000)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
