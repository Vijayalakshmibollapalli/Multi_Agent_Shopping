import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing on the MCP server."}]
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]

def clean_results(results: list, limit: int = 5000) -> str:
    cleaned = [{"title": str(x.get("title", "")).strip(), "url": str(x.get("url", "")).strip(), "content": str(x.get("content", "")).strip()} for x in results]
    return json.dumps(cleaned, ensure_ascii=False)[:limit]

@mcp.tool
def search_products(query: str) -> str:
    return clean_results(search_web(f"{query} best products exact models specifications India 2026", 5), 5000)

@mcp.tool
def search_prices(query: str) -> str:
    return clean_results(search_web(f"{query} current price India buy price Amazon Flipkart Croma official store 2026", 5), 5000)

@mcp.tool
def search_reviews(query: str) -> str:
    return clean_results(search_web(f"{query} reviews ratings pros cons customer experience India 2026", 5), 4000)

@mcp.tool
def search_comparison(query: str) -> str:
    return clean_results(search_web(f"{query} comparison alternatives competing products India 2026", 5), 4000)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
