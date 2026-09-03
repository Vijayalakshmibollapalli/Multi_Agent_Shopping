import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY: raise RuntimeError("TAVILY_API_KEY is missing in .env")

mcp = FastMCP("AI Shopping Intelligence MCP Server")
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def search(query: str, n: int = 6) -> list:
    try:
        response = tavily.search(query=query, max_results=n, search_depth="advanced", include_answer=False)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "SEARCH_ERROR", "url": "", "content": str(e)}]

def format_data(results: list, limit: int = 5000) -> str:
    output = []
    total = 0
    for i, result in enumerate(results, 1):
        title = str(result.get("title", "")).strip()
        url = str(result.get("url", "")).strip()
        content = str(result.get("content", "")).strip()[:1800]
        item = f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}"
        if total + len(item) > limit: break
        output.append(item)
        total += len(item)
    return "\n\n".join(output)

@mcp.tool
def search_products(query: str) -> str:
    """Find real products, exact models and relevant specifications for any shopping category."""
    return format_data(search(f"{query} real products India exact model names specifications features current models", 6), 5000)

@mcp.tool
def search_prices(query: str) -> str:
    """Find current product prices and availability in India."""
    return format_data(search(f"{query} India current price online price Amazon Flipkart Croma Reliance Digital official store availability", 6), 4500)

@mcp.tool
def search_reviews(query: str) -> str:
    """Find product reviews, ratings, user experience, pros, cons and common problems."""
    return format_data(search(f"{query} India expert reviews user reviews ratings pros cons problems reliability performance", 6), 4500)

@mcp.tool
def search_comparison(query: str) -> str:
    """Find competitors, alternatives, comparisons, specifications and performance differences."""
    return format_data(search(f"{query} comparison alternatives competitors similar products specifications price advantages disadvantages India", 5), 3500)

if __name__ == "__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    print("Tavily API configured successfully.")
    print("MCP server running on http://0.0.0.0:8000")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
