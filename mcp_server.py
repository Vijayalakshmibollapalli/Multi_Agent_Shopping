import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is missing in .env")

mcp = FastMCP("AI Shopping Intelligence MCP Server")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def search(query: str, n: int = 8) -> list:
    try:
        response = tavily.search(query=query, max_results=n, search_depth="advanced", include_answer=False, include_raw_content=False)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "SEARCH_ERROR", "url": "", "content": str(e)}]

def format_data(results: list, limit: int = 6500) -> str:
    output = []
    total = 0
    for i, result in enumerate(results, 1):
        title = str(result.get("title", "")).strip()
        url = str(result.get("url", "")).strip()
        content = str(result.get("content", "")).strip()[:2200]
        item = f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}"
        if total + len(item) > limit:
            break
        output.append(item)
        total += len(item)
    return "\n\n".join(output)

@mcp.tool
def search_products(query: str) -> str:
    """Find real purchasable products from any shopping category with exact product names, brands, models, variants and relevant specifications."""
    return format_data(search(f"{query} real purchasable products India exact product names brands models variants specifications features current products", 8), 6000)

@mcp.tool
def search_prices(query: str) -> str:
    """Find current prices and availability for products from any shopping category in India."""
    return format_data(search(f"{query} India current price online price availability official store Amazon Flipkart Croma Reliance Digital Myntra retailer", 8), 5500)

@mcp.tool
def search_reviews(query: str) -> str:
    """Find expert reviews, user reviews, ratings, customer feedback, pros, cons, quality, reliability and common problems for any product category."""
    return format_data(search(f"{query} India expert reviews user reviews ratings customer feedback pros cons quality reliability common problems performance", 8), 5500)

@mcp.tool
def search_comparison(query: str) -> str:
    """Find competing products, alternatives and comparable products from the same shopping category."""
    return format_data(search(f"{query} comparison alternatives competitors similar products differences specifications price advantages disadvantages India", 8), 4500)

if __name__ == "__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    print("Tavily API configured successfully.")
    print("MCP server running on http://0.0.0.0:8000")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
