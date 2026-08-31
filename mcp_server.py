import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

# --------------------------------------------------
# MCP SERVER
# --------------------------------------------------

mcp = FastMCP("AI Shopping Intelligence MCP Server")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is missing in .env")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# --------------------------------------------------
# SEARCH HELPER
# --------------------------------------------------

def search_web(query: str, max_results: int = 3):
    """
    Perform a compact Tavily search.
    Only a small amount of information is returned
    to prevent large LLM contexts.
    """

    try:
        response = tavily.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False
        )

        results = []

        for item in response.get("results", [])[:max_results]:

            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:700]
            })

        return results

    except Exception as e:

        return [{
            "title": "SEARCH_ERROR",
            "url": "",
            "content": str(e)
        }]


# --------------------------------------------------
# FORMAT HELPER
# --------------------------------------------------

def format_results(results, max_chars=2500):

    output = []
    total = 0

    for index, item in enumerate(results, 1):

        text = (
            f"[SOURCE {index}]\n"
            f"Title: {item.get('title', '')}\n"
            f"URL: {item.get('url', '')}\n"
            f"Information: {item.get('content', '')[:600]}"
        )

        if total + len(text) > max_chars:
            break

        output.append(text)

        total += len(text)

    return "\n\n".join(output)


# --------------------------------------------------
# TOOL 1
# --------------------------------------------------

@mcp.tool
def search_products(query: str) -> str:
    """
    Find real products matching the user's shopping requirement.
    """

    results = search_web(
        f"{query} products India specifications models",
        3
    )

    return format_results(results, 2200)


# --------------------------------------------------
# TOOL 2
# --------------------------------------------------

@mcp.tool
def search_prices(query: str) -> str:
    """
    Find current prices for products in India.
    """

    results = search_web(
        f"{query} current price India Amazon Flipkart Croma Reliance Digital",
        3
    )

    return format_results(results, 2200)


# --------------------------------------------------
# TOOL 3
# --------------------------------------------------

@mcp.tool
def search_reviews(query: str) -> str:
    """
    Find reviews, pros, cons and customer feedback.
    """

    results = search_web(
        f"{query} reviews pros cons customer feedback problems India",
        3
    )

    return format_results(results, 2200)


# --------------------------------------------------
# TOOL 4
# --------------------------------------------------

@mcp.tool
def search_comparison(query: str) -> str:
    """
    Find product comparisons and alternatives.
    """

    results = search_web(
        f"{query} comparison alternatives advantages disadvantages",
        2
    )

    return format_results(results, 1800)


# --------------------------------------------------
# START MCP SERVER
# --------------------------------------------------

if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000
    )
