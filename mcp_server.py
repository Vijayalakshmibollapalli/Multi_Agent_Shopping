import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()
mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=6):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=4500):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        source=f"[SOURCE {i}]\nTitle: {item.get('title','')}\nURL: {item.get('url','')}\nContent: {item.get('content','')[:1200]}\n"
        if total+len(source)>limit: break
        output.append(source)
        total+=len(source)
    return "\n".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant product models and available product options."""
    return format_results(search(f"{query} product models features specifications",6),4200)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications and product information."""
    return format_results(search(f"{query} official manufacturer specifications product features",6),4200)

@mcp.tool
def search_prices(query:str):
    """Find current prices and availability from retailers and stores."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital",6),4200)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, pros, cons and reported problems."""
    return format_results(search(f"{query} expert review user reviews pros cons problems",6),4200)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons between products and alternative recommendations."""
    return format_results(search(f"{query} comparison versus alternatives advantages disadvantages",6),4000)

@mcp.tool
def search_web(query:str):
    """Search broader web sources for relevant product information."""
    return format_results(search(f"{query} latest information buying guide review comparison",6),4000)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube product reviews, demonstrations, comparisons and unboxing videos."""
    return format_results(search(f"site:youtube.com {query} review comparison demonstration unboxing",6),3500)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
