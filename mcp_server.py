import os
from tavily import TavilyClient
from fastmcp import FastMCP

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 3) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "CONFIGURATION_ERROR", "url": "", "content": "TAVILY_API_KEY is not configured on the remote server."}]
    try:
        tavily = TavilyClient(api_key=api_key)
        result = tavily.search(query=query, search_depth="basic", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "SEARCH_ERROR", "url": "", "content": str(e)}]

def compact_results(results: list, limit: int = 2000) -> str:
    output = []
    total = 0
    for i, item in enumerate(results, 1):
        title = str(item.get("title", ""))[:150]
        url = str(item.get("url", ""))[:250]
        content = str(item.get("content", ""))[:400]
        text = f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}"
        if total + len(text) > limit:
            break
        output.append(text)
        total += len(text)
    return "\n\n".join(output)

@mcp.tool
def search_products(query: str) -> str:
    """Find real products matching the user's requirements."""
    return compact_results(search_web(f"{query} products India specifications models", 3), 2000)

@mcp.tool
def search_prices(query: str) -> str:
    """Find current product prices and availability in India."""
    return compact_results(search_web(f"{query} current price India Amazon Flipkart Croma official store", 3), 2000)

@mcp.tool
def search_reviews(query: str) -> str:
    """Find product reviews, pros, cons and customer feedback."""
    return compact_results(search_web(f"{query} reviews pros cons customer feedback problems", 3), 2000)

@mcp.tool
def search_comparison(query: str) -> str:
    """Find product comparisons and alternatives."""
    return compact_results(search_web(f"{query} comparison alternatives advantages disadvantages", 3), 1600)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
