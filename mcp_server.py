import os,json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=4):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return [{"title":x.get("title",""),"url":x.get("url",""),"content":x.get("content","")[:700]} for x in result.get("results",[])]
    except Exception as e:
        return [{"title":"Search Error","url":"","content":str(e)}]

def result(query,source_type):
    return json.dumps({"source_type":source_type,"results":search(query)},ensure_ascii=False)

@mcp.tool
def search_products(query:str):
    """Find relevant product models and product options."""
    return result(f"{query} product models best options", "Products")

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return result(f"{query} official manufacturer specifications", "Official Specifications")

@mcp.tool
def search_prices(query:str):
    """Find current product prices and availability."""
    return result(f"{query} current price India retailer Amazon Flipkart Croma Reliance Digital", "Prices")

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, advantages and problems."""
    return result(f"{query} expert review user review pros cons problems", "Reviews")

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternative products."""
    return result(f"{query} comparison versus alternatives", "Comparisons")

@mcp.tool
def search_web(query:str):
    """Find additional relevant information from the web."""
    return result(f"{query} latest information buying guide", "Web")

@mcp.tool
def search_youtube(query:str):
    """Find relevant YouTube reviews, comparisons and demonstrations."""
    return result(f"site:youtube.com {query} review comparison demonstration unboxing", "YouTube")

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
