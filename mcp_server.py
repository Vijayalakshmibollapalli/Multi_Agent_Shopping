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
        return [
            {
                "title": "TAVILY ERROR",
                "url": "",
                "content": "TAVILY_API_KEY is missing."
            }
        ]

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False
        )

        return response.get("results", [])

    except Exception as e:
        return [
            {
                "title": "TAVILY ERROR",
                "url": "",
                "content": str(e)
            }
        ]


def clean_results(
    results: list,
    max_items: int = 5,
    max_content: int = 1500
) -> str:

    cleaned = []

    for item in results[:max_items]:

        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        content = str(item.get("content", "")).strip()

        if title or content:

            cleaned.append(
                {
                    "title": title[:400],
                    "url": url[:700],
                    "content": content[:max_content]
                }
            )

    return json.dumps(
        cleaned,
        ensure_ascii=False
    )


@mcp.tool
def search_products(query: str) -> str:
    """
    Discover real products and exact product models for any shopping category.
    """

    search_query = f"""
    {query}

    Find real products currently available in India.
    Identify exact product names, brands and model names.
    Include relevant specifications, features, variants and product details.
    Prefer current products and trustworthy sources.
    Do not restrict the search to electronics.
    """

    return clean_results(
        search_web(search_query, 6),
        max_items=6,
        max_content=1500
    )


@mcp.tool
def search_prices(query: str) -> str:
    """
    Find current prices and availability for a specific product in India.
    """

    search_query = f"""
    {query}

    Find the current price and availability in India.
    Search online retailers, official stores and reliable product sources.
    Look specifically for the exact product or model mentioned in the query.
    Include seller and price information when available.
    """

    return clean_results(
        search_web(search_query, 6),
        max_items=6,
        max_content=1500
    )


@mcp.tool
def search_reviews(query: str) -> str:
    """
    Find reviews, ratings, user experience, strengths, weaknesses
    and reliability information for a specific product.
    """

    search_query = f"""
    {query}

    Find reviews and user experiences for this exact product.
    Look for strengths, weaknesses, reliability, performance,
    durability, comfort, usability and common complaints.
    Prefer trustworthy review sources and user feedback.
    """

    return clean_results(
        search_web(search_query, 6),
        max_items=6,
        max_content=1500
    )


@mcp.tool
def search_comparison(query: str) -> str:
    """
    Find competitors, alternatives and product comparisons
    for any shopping category.
    """

    search_query = f"""
    {query}

    Find competing products and alternatives.
    Compare important specifications, features, price,
    performance, usability and value.
    Do not assume the product category is electronics.
    """

    return clean_results(
        search_web(search_query, 6),
        max_items=6,
        max_content=1500
    )


if __name__ == "__main__":

    print("=" * 60)
    print("Starting AI Shopping Intelligence MCP Server")
    print("=" * 60)
    print("Transport : streamable-http")
    print("Host      : 0.0.0.0")
    print("Port      : 8000")
    print("=" * 60)

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
