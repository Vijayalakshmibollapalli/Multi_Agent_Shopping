import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence MCP Server")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 4):
    try:
        response = tavily.search(query=query, search_depth="basic", max_results=max_results)
        results = response.get("results", [])
        clean_results = []
        for item in results: clean_results.append({"title": item.get("title", ""), "content": item.get("content", "")[:1200], "url": item.get("url", "")})
        return clean_results
    except Exception as e: return [{"error": str(e)}]

@mcp.tool
def search_products(query: str) -> str:
    """Find possible products for any shopping request."""
    return json.dumps(search_web(f"{query} best product models specifications", 5), ensure_ascii=False)

@mcp.tool
def search_product_details(product: str) -> str:
    """Find important product features and details."""
    return json.dumps(search_web(f"{product} features specifications details", 3), ensure_ascii=False)

@mcp.tool
def search_official_specs(product: str) -> str:
    """Find official specifications."""
    return json.dumps(search_web(f"{product} official specifications", 3), ensure_ascii=False)

@mcp.tool
def search_prices(product: str) -> str:
    """Find approximate current prices."""
    return json.dumps(search_web(f"{product} price India", 3), ensure_ascii=False)

@mcp.tool
def search_reviews(product: str) -> str:
    """Find reviews and opinions."""
    return json.dumps(search_web(f"{product} review pros cons", 3), ensure_ascii=False)

@mcp.tool
def search_comparison(products: str) -> str:
    """Compare multiple products."""
    return json.dumps(search_web(f"compare {products}", 4), ensure_ascii=False)

if __name__ == "__main__": mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
