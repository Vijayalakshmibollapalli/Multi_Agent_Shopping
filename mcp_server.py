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
        response = tavily.search(query=query, search_depth="basic", max_results=max_results, include_answer=False)
        results = []
        for item in response.get("results", []):
            results.append({"title": item.get("title", ""), "content": item.get("content", "")[:700], "url": item.get("url", "")})
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool
def search_products(query: str) -> str:
    return json.dumps(search_web(f"India purchasable {query} exact product model current price specifications", 6), ensure_ascii=False)

@mcp.tool
def search_product_details(product: str) -> str:
    return json.dumps(search_web(f'"{product}" India official specifications processor RAM storage display features', 3), ensure_ascii=False)

@mcp.tool
def search_prices(product: str) -> str:
    return json.dumps(search_web(f'"{product}" India current price INR Amazon Flipkart official store', 3), ensure_ascii=False)

@mcp.tool
def search_reviews(product: str) -> str:
    return json.dumps(search_web(f'"{product}" India customer reviews pros cons performance', 3), ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
