import os
from tavily import TavilyClient
from fastmcp import FastMCP
mcp = FastMCP(name="AI Shopping Intelligence")
def search_web(query: str, max_results: int = 2) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the remote MCP server."}]
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]
def compact_results(results: list, limit: int = 1000) -> str:
    output = []
    for i, item in enumerate(results, 1):
        output.append(f"[SOURCE {i}]\nTitle: {str(item.get('title', ''))[:120]}\nURL: {str(item.get('url', ''))[:200]}\nContent: {str(item.get('content', ''))[:300]}")
    return "\n\n".join(output)[:limit]
@mcp.tool
def search_products(query: str) -> str:
    return compact_results(search_web(f"{query} India best products specifications models 2026", 2))
@mcp.tool
def search_prices(query: str) -> str:
    return compact_results(search_web(f"{query} India current price Amazon India Flipkart Croma official 2026", 2))
@mcp.tool
def search_reviews(query: str) -> str:
    return compact_results(search_web(f"{query} India reviews pros cons customer feedback 2026", 2))
@mcp.tool
def search_comparison(query: str) -> str:
    return compact_results(search_web(f"{query} India comparison alternatives best products 2026", 2))
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
