import os
from tavily import TavilyClient
from fastmcp import FastMCP

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 4) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the remote MCP server."}]
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]

def compact_results(results: list, limit: int = 2200) -> str:
    output = []
    for i, item in enumerate(results, 1):
        title = str(item.get("title", ""))[:180]
        url = str(item.get("url", ""))[:300]
        content = str(item.get("content", ""))[:550]
        output.append(f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}")
    return "\n\n".join(output)[:limit]

@mcp.tool
def search_products(query: str) -> str:
    """Find specific real product models matching the user's requirements with specifications."""
    search_query = f"{query} India best product models exact model names processor RAM storage specifications buy 2026"
    return compact_results(search_web(search_query, 4))

@mcp.tool
def search_prices(query: str) -> str:
    """Find specific product model names with current India prices and availability."""
    search_query = f"{query} India exact product model current price ₹ Amazon Flipkart Croma Reliance Digital Vijay Sales official store 2026"
    return compact_results(search_web(search_query, 4))

@mcp.tool
def search_reviews(query: str) -> str:
    """Find pros, cons, problems and customer or expert reviews for suitable products."""
    search_query = f"{query} best models review pros cons performance battery display heating customer feedback India 2026"
    return compact_results(search_web(search_query, 4))

@mcp.tool
def search_comparison(query: str) -> str:
    """Find specific alternative product models and comparisons."""
    search_query = f"{query} India best alternatives comparison exact models versus top picks 2026"
    return compact_results(search_web(search_query, 4))

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
