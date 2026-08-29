import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence MCP Server")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 6):
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=max_results)
        return response.get("results", [])
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool
def search_products(query: str) -> str:
    """Find possible products for any shopping request."""
    return json.dumps(search_web(f"{query} best products models specifications price", 8), ensure_ascii=False)

@mcp.tool
def search_product_details(product: str) -> str:
    """Find detailed information and features for a product."""
    return json.dumps(search_web(f"{product} specifications features official details", 6), ensure_ascii=False)

@mcp.tool
def search_official_specs(product: str) -> str:
    """Find official specifications of a product."""
    return json.dumps(search_web(f"{product} official specifications manufacturer site", 6), ensure_ascii=False)

@mcp.tool
def search_prices(product: str) -> str:
    """Find current prices and seller information."""
    return json.dumps(search_web(f"{product} price India Amazon Flipkart Croma Reliance", 6), ensure_ascii=False)

@mcp.tool
def search_reviews(product: str) -> str:
    """Find expert reviews and user opinions."""
    return json.dumps(search_web(f"{product} review pros cons user reviews", 6), ensure_ascii=False)

@mcp.tool
def search_comparison(products: str) -> str:
    """Compare multiple products separated by commas."""
    return json.dumps(search_web(f"compare {products} specifications price review pros cons", 8), ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
