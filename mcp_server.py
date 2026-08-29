import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence MCP Server")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 3):
    try:
        response = tavily.search(query=query, search_depth="basic", max_results=max_results)
        results = response.get("results", [])
        return [{"title":item.get("title",""),"content":item.get("content","")[:900],"url":item.get("url","")} for item in results]
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query: str) -> str:
    """Find possible products for any shopping request."""
    return json.dumps(search_web(f"{query} best product models specifications India",5),ensure_ascii=False)

@mcp.tool
def search_product_details(product: str) -> str:
    """Find important product features and details."""
    return json.dumps(search_web(f"{product} features specifications details",2),ensure_ascii=False)

@mcp.tool
def search_official_specs(product: str) -> str:
    """Find official specifications."""
    return json.dumps(search_web(f"{product} official specifications manufacturer",2),ensure_ascii=False)

@mcp.tool
def search_prices(product: str) -> str:
    """Find current product prices."""
    return json.dumps(search_web(f"{product} price India",2),ensure_ascii=False)

@mcp.tool
def search_reviews(product: str) -> str:
    """Find reviews, pros and cons."""
    return json.dumps(search_web(f"{product} review pros cons",2),ensure_ascii=False)

@mcp.tool
def search_comparison(products: str) -> str:
    """Compare multiple products."""
    return json.dumps(search_web(f"compare {products} specifications pros cons",3),ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
