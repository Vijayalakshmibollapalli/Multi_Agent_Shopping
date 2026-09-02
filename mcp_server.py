import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")


def search_web(query: str, max_results: int = 6) -> list:
    key = os.getenv("TAVILY_API_KEY")

    if not key:
        return [{
            "title": "TAVILY ERROR",
            "url": "",
            "content": "TAVILY_API_KEY is missing"
        }]

    try:
        client = TavilyClient(api_key=key)

        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )

        return result.get("results", [])

    except Exception as e:
        return [{
            "title": "TAVILY ERROR",
            "url": "",
            "content": str(e)
        }]


def clean_results(results: list) -> str:
    cleaned = []

    for item in results[:6]:

        if not isinstance(item, dict):
            continue

        title = str(
            item.get("title", "")
        ).strip()

        url = str(
            item.get("url", "")
        ).strip()

        content = str(
            item.get("content", "")
        ).strip()

        if not title and not content:
            continue

        cleaned.append({
            "title": title[:400],
            "url": url,
            "content": content[:2200]
        })

    return json.dumps(
        cleaned,
        ensure_ascii=False
    )


@mcp.tool
def search_products(query: str) -> str:

    search_query = (
        f"{query} "
        f"best products exact models specifications "
        f"features India"
    )

    return clean_results(
        search_web(
            search_query,
            6
        )
    )


@mcp.tool
def search_prices(query: str) -> str:

    search_query = (
        f"{query} "
        f"current price India "
        f"Amazon Flipkart Croma "
        f"official store price"
    )

    return clean_results(
        search_web(
            search_query,
            6
        )
    )


@mcp.tool
def search_reviews(query: str) -> str:

    search_query = (
        f"{query} "
        f"reviews ratings "
        f"pros cons customer experience "
        f"India"
    )

    return clean_results(
        search_web(
            search_query,
            6
        )
    )


@mcp.tool
def search_comparison(query: str) -> str:

    search_query = (
        f"{query} "
        f"comparison alternatives "
        f"competing products "
        f"India"
    )

    return clean_results(
        search_web(
            search_query,
            6
        )
    )


if __name__ == "__main__":

    print(
        "Starting AI Shopping Intelligence MCP Server..."
    )

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
