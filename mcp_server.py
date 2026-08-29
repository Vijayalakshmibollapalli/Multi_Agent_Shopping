import os
import re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()

def valid_url(url):
    url=clean(url).replace("\\n","").replace("\n","")
    return url.startswith("http://") or url.startswith("https://")

def search(query,n=5):
    try:
        results=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
        return [{"title":clean(x.get("title","")),"url":clean(x.get("url","")),"content":clean(x.get("content",""))} for x in results if clean(x.get("title","")) and valid_url(x.get("url",""))]
    except Exception: return []

def clean_results(results,limit=6):
    return [{"title":x["title"][:200],"url":x["url"],"content":x["content"][:1200]} for x in results[:limit]]

@mcp.tool
def search_products(query:str):
    """Find real purchasable product models matching the user's request."""
    return clean_results(search(f"{query} best exact laptop models India buy",8),8)

@mcp.tool
def search_product_details(product:str):
    """Find specifications for one exact product model."""
    return clean_results(search(f'"{product}" specifications processor RAM storage display',6),6)

@mcp.tool
def search_official_specs(product:str):
    """Find official manufacturer specifications for an exact product."""
    return clean_results(search(f'"{product}" official specifications manufacturer',6),6)

@mcp.tool
def search_prices(product:str):
    """Find current Indian prices for an exact product."""
    return clean_results(search(f'"{product}" price India ₹ buy Amazon Flipkart Croma',6),6)

@mcp.tool
def search_reviews(product:str):
    """Find reviews and user feedback for an exact product."""
    return clean_results(search(f'"{product}" review pros cons',5),5)

@mcp.tool
def search_comparison(product:str):
    """Find alternatives or comparisons for an exact product."""
    return clean_results(search(f'"{product}" alternatives comparison',5),5)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
