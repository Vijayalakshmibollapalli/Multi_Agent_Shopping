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

def search(query,n=6):
    try:
        results=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
        output=[]
        for item in results:
            title=clean(item.get("title",""))
            url=clean(item.get("url",""))
            content=clean(item.get("content",""))
            if title and valid_url(url): output.append({"title":title,"url":url,"content":content[:1500]})
        return output
    except Exception as e:
        print(f"Search error: {e}")
        return []

@mcp.tool
def search_products(query:str):
    """Find real purchasable product models for ANY type of product requested by the user."""
    return search(f"{query} exact product models available India buy",8)

@mcp.tool
def search_product_details(product:str):
    """Find specifications, features and configuration for one exact product."""
    return search(f'"{product}" specifications features configuration',6)

@mcp.tool
def search_official_specs(product:str):
    """Find official manufacturer specifications for one exact product."""
    return search(f'"{product}" official manufacturer specifications',6)

@mcp.tool
def search_prices(product:str):
    """Find current prices and sellers in India for one exact product."""
    return search(f'"{product}" price India buy Flipkart Amazon Croma Reliance',6)

@mcp.tool
def search_reviews(product:str):
    """Find professional and user reviews for one exact product."""
    return search(f'"{product}" review pros cons user experience',5)

@mcp.tool
def search_comparison(product:str):
    """Find competing products and alternatives for comparison."""
    return search(f'"{product}" alternatives competitors comparison',5)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
