import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence MCP Server")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web(query, max_results=5):
    try:
        data = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )

        results = []

        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "content": item.get("content", "")[:800],
                "url": item.get("url", "")
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
def search_products(query: str) -> str:
    search_query = f"""
    {query}
    India
    individual exact product models
    product name model number price specifications
    do not return only list articles
    """
    return json.dumps(search_web(search_query, 8), ensure_ascii=False)


@mcp.tool
def search_product_details(product: str) -> str:
    query = f'"{product}" exact model features specifications'
    return json.dumps(search_web(query, 4), ensure_ascii=False)


@mcp.tool
def search_official_specs(product: str) -> str:
    query = f'"{product}" official specifications manufacturer'
    return json.dumps(search_web(query, 4), ensure_ascii=False)


@mcp.tool
def search_prices(product: str) -> str:
    query = f'"{product}" price India Amazon Flipkart Croma Reliance Digital'
    return json.dumps(search_web(query, 4), ensure_ascii=False)


@mcp.tool
def search_reviews(product: str) -> str:
    query = f'"{product}" review pros cons performance'
    return json.dumps(search_web(query, 4), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
