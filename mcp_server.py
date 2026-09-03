import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_web(query: str, max_results: int = 4) -> list:
    if not TAVILY_API_KEY:
        return [{"title": "TAVILY ERROR", "url": "", "content": "TAVILY_API_KEY is missing"}]
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, search_depth="basic", max_results=max_results, include_answer=False)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY ERROR", "url": "", "content": str(e)}]

def clean_results(results: list, max_items: int = 4, max_content: int = 700) -> str:
    cleaned = []
    for item in results[:max_items]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        content = str(item.get("content", "")).strip()
        if title or content:
            cleaned.append({"title": title[:250], "url": url[:400], "content": content[:max_content]})
    return json.dumps(cleaned, ensure_ascii=False)

@mcp.tool
def search_products(query: str) -> str:
    """Search real products and specifications for any shopping request."""
    search_query = f"{query} real product models specifications features India"
    return clean_results(search_web(search_query, 4), 4, 700)

@mcp.tool
def search_prices(query: str) -> str:
    """Search current prices for products matching any shopping request."""
    search_query = f"{query} current price India online price Amazon Flipkart Croma official store"
    return clean_results(search_web(search_query, 4), 4, 700)

@mcp.tool
def search_reviews(query: str) -> str:
    """Search reviews, ratings, pros and cons for products matching any shopping request."""
    search_query = f"{query} customer reviews ratings pros cons user experience reliability"
    return clean_results(search_web(search_query, 4), 4, 700)

@mcp.tool
def search_comparison(query: str) -> str:
    """Search real competing products and alternatives for any shopping request."""
    search_query = f"{query} product comparison alternatives competing models specifications price India"
    return clean_results(search_web(search_query, 4), 4, 700)

if __name__ == "__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
