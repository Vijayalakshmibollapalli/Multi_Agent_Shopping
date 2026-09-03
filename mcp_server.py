import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_web(query: str, max_results: int = 5) -> list:
    if not TAVILY_API_KEY:
        return [{"title": "TAVILY ERROR", "url": "", "content": "TAVILY_API_KEY is missing"}]
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY ERROR", "url": "", "content": str(e)}]

def clean_results(results: list, max_items: int = 5, max_content: int = 1200) -> str:
    cleaned = []
    for item in results[:max_items]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        content = str(item.get("content", "")).strip()
        if title or content:
            cleaned.append({"title": title[:300], "url": url[:600], "content": content[:max_content]})
    return json.dumps(cleaned, ensure_ascii=False)

@mcp.tool
def search_products(query: str) -> str:
    """Find real products and exact models matching any shopping request."""
    search_query = f"{query} best products exact model names specifications features India"
    return clean_results(search_web(search_query, 5), 5, 1200)

@mcp.tool
def search_prices(query: str) -> str:
    """Find current prices and availability for any product in India."""
    search_query = f"{query} current price India online price Amazon Flipkart Croma Reliance Digital official store"
    return clean_results(search_web(search_query, 5), 5, 1200)

@mcp.tool
def search_reviews(query: str) -> str:
    """Find reviews ratings user experience pros cons reliability performance for any product."""
    search_query = f"{query} reviews ratings user experience pros cons reliability performance India"
    return clean_results(search_web(search_query, 5), 5, 1200)

@mcp.tool
def search_comparison(query: str) -> str:
    """Find comparisons competitors alternatives specifications price and performance."""
    search_query = f"{query} comparison alternatives competitors specifications price performance India"
    return clean_results(search_web(search_query, 5), 5, 1200)

if __name__ == "__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
