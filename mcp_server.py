import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is missing")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str, max_results: int = 3) -> list:
    try:
        result = tavily.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False
        )

        return result.get("results", [])

    except Exception as e:
        return [
            {
                "title": "SEARCH_ERROR",
                "url": "",
                "content": str(e)
            }
        ]


def compact_results(results: list, limit: int = 3000) -> str:
    output = []
    total = 0

    for i, item in enumerate(results, 1):

        title = str(item.get("title", ""))[:200]
        url = str(item.get("url", ""))[:300]
        content = str(item.get("content", ""))[:600]

        text = (
            f"[SOURCE {i}]\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content: {content}"
        )

        if total + len(text) > limit:
            break

        output.append(text)
        total += len(text)

    return "\n\n".join(output)


@mcp.tool
def search_products(query: str) -> str:
    """
    Find real products matching the user's requirements.
    """

    results = search_web(
        f"{query} products India specifications models",
        3
    )

    return compact_results(results, 3000)


@mcp.tool
def search_prices(query: str) -> str:
    """
    Find current product prices and availability in India.
    """

    results = search_web(
        f"{query} current price India Amazon Flipkart Croma official store",
        3
    )

    return compact_results(results, 3000)


@mcp.tool
def search_reviews(query: str) -> str:
    """
    Find product reviews, pros, cons and customer feedback.
    """

    results = search_web(
        f"{query} reviews pros cons customer feedback problems",
        3
    )

    return compact_results(results, 3000)


@mcp.tool
def search_comparison(query: str) -> str:
    """
    Find comparisons and alternatives for products.
    """

    results = search_web(
        f"{query} comparison alternatives advantages disadvantages",
        3
    )

    return compact_results(results, 2500)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
