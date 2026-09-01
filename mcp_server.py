import os
from tavily import TavilyClient
from fastmcp import FastMCP

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the remote MCP server."}]
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]

def compact_results(results: list, limit: int = 4500) -> str:
    output = []
    for i, item in enumerate(results, 1):
        output.append(f"[SOURCE {i}]\nTitle: {str(item.get('title', ''))[:180]}\nURL: {str(item.get('url', ''))[:350]}\nContent: {str(item.get('content', ''))[:700]}")
    return "\n\n".join(output)[:limit]

@mcp.tool
def search_products(query: str) -> str:
    """Find real products matching the user's requirements."""
    return compact_results(search_web(f"{query} India best laptop product model specifications 2026", 5))

@mcp.tool
def search_prices(query: str) -> str:
    """Find current product prices and availability in India."""
    return compact_results(search_web(f"{query} India current price ₹ price Amazon India Flipkart Croma official website 2026", 5))

@mcp.tool
def search_reviews(query: str) -> str:
    """Find product reviews, pros, cons and customer feedback."""
    return compact_results(search_web(f"{query} India reviews pros cons customer feedback problems 2026", 5))

@mcp.tool
def search_comparison(query: str) -> str:
    """Find product comparisons and alternatives."""
    return compact_results(search_web(f"{query} India comparison alternatives best products 2026", 5))

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
