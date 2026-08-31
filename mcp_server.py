import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP(name="AI Shopping Intelligence MCP Server")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query, max_results=4):
    try:
        response = tavily.search(query=query, search_depth="basic", max_results=max_results, include_answer=False)
        results = []
        for item in response.get("results", []):
            results.append({"title": item.get("title", "")[:160], "content": item.get("content", "")[:600], "url": item.get("url", "")})
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool
def search_products(query: str) -> str:
    search_query = f"India buy {query} exact product models laptop phone monitor headphones washing machine office chair current products"
    return json.dumps(search_web(search_query, 6), ensure_ascii=False)

@mcp.tool
def search_product_details(product: str) -> str:
    search_query = f'"{product}" specifications processor RAM storage display features India'
    return json.dumps(search_web(search_query, 3), ensure_ascii=False)

@mcp.tool
def search_prices(product: str) -> str:
    search_query = f'"{product}" price India INR current Amazon Flipkart official'
    return json.dumps(search_web(search_query, 3), ensure_ascii=False)

@mcp.tool
def search_reviews(product: str) -> str:
    search_query = f'"{product}" review rating pros cons customer experience India'
    return json.dumps(search_web(search_query, 3), ensure_ascii=False)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
