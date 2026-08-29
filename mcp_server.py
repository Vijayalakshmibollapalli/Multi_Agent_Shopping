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
        output=[]
        for item in results:
            title=clean(item.get("title",""))
            url=clean(item.get("url",""))
            content=clean(item.get("content",""))
            if title and valid_url(url): output.append({"title":title,"url":url,"content":content})
        return output
    except Exception:
        return []

def clean_results(results,limit=6):
    output=[]
    for item in results[:limit]:
        output.append({"title":item["title"][:200],"url":item["url"],"content":item["content"][:1200]})
    return output

@mcp.tool
def search_products(query:str):
    """Find real purchasable product models matching the user's request."""
    return clean_results(search(f"{query} exact product models India",8),8)

@mcp.tool
def search_product_details(product:str):
    """Find specifications for one exact product model."""
    return clean_results(search(f'"{product}" specifications processor RAM storage display',6),6)

@mcp.tool
def search_official_specs(product:str):
    """Find official manufacturer specifications for an exact product."""
    results=search(f'"{product}" official specifications manufacturer',6)
    return clean_results(results,6)

@mcp.tool
def search_prices(product:str):
    """Find current Indian prices for an exact product."""
    return clean_results(search(f'"{product}" price India buy',6),6)

@mcp.tool
def search_reviews(product:str):
    """Find reviews and user feedback for an exact product."""
    return clean_results(search(f'"{product}" review pros cons',5),5)

@mcp.tool
def search_comparison(product:str):
    """Find alternatives or comparisons for an exact product."""
    return clean_results(search(f'"{product}" alternatives comparison',5),5)

@mcp.tool
def search_web(product:str):
    """Find additional reliable information for an exact product."""
    return clean_results(search(f'"{product}" specifications features India',5),5)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
