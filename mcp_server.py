import os,json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()
mcp=FastMCP(name="AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query,max_results=3):
    try:
        data=tavily.search(query=query,search_depth="basic",max_results=max_results)
        return [{"title":x.get("title",""),"content":x.get("content","")[:700],"url":x.get("url","")} for x in data.get("results",[])]
    except Exception as e:return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    """Find real product models matching the shopping request."""
    return json.dumps(search_web(f"{query} best models India specifications price",5),ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    """Find product details."""
    return json.dumps(search_web(f'"{product}" features specifications',3),ensure_ascii=False)

@mcp.tool
def search_official_specs(product:str)->str:
    """Find verified product specifications."""
    return json.dumps(search_web(f'"{product}" official specifications',3),ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    """Find current product prices in India."""
    return json.dumps(search_web(f'"{product}" price India',3),ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    """Find reviews, pros and cons."""
    return json.dumps(search_web(f'"{product}" review pros cons',3),ensure_ascii=False)

@mcp.tool
def search_comparison(products:str)->str:
    """Compare multiple products."""
    return json.dumps(search_web(f"{products} comparison specifications pros cons",3),ensure_ascii=False)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT",8000)))
