import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

def search_web(query: str, max_results: int = 5) -> list:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return [{"title": "ERROR", "url": "", "content": "TAVILY_API_KEY is missing"}]
    try:
        client = TavilyClient(api_key=key)
        result = client.search(query=query, search_depth="advanced", max_results=max_results, include_answer=False)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "TAVILY_ERROR", "url": "", "content": str(e)}]

def clean_results(results: list) -> str:
    cleaned = []
    for x in results[:5]:
        cleaned.append({"title": str(x.get("title", "")).strip()[:250], "url": str(x.get("url", "")).strip(), "content": str(x.get("content", "")).strip()[:1400]})
    return json.dumps(cleaned, ensure_ascii=False)

@mcp.tool
def search_products(query: str) -> str:
    return clean_results(search_web(f"{query} best products exact models specifications India current", 5))

@mcp.tool
def search_prices(query: str) -> str:
    return clean_results(search_web(f"{query} current price India Amazon Flipkart Croma official store", 5))

@mcp.tool
def search_reviews(query: str) -> str:
    return clean_results(search_web(f"{query} reviews ratings pros cons customer experience India", 5))

@mcp.tool
def search_comparison(query: str) -> str:
    return clean_results(search_web(f"{query} comparison alternatives competing products India", 5))

if __name__ == "__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
