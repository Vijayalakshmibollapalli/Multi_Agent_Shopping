import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=5):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"Search Error","url":"","content":str(e)}]

def format_results(results,limit=2500):
    output=[]
    total=0
    for item in results:
        content=item.get("content","")[:500]
        text=f"TITLE: {item.get('title','')}\nURL: {item.get('url','')}\nCONTENT: {content}\n\n"
        if total+len(text)>limit:
            break
        output.append(text)
        total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant product models and available options."""
    return format_results(search(f"{query} best product models specifications",5),2500)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return format_results(search(f"{query} official manufacturer specifications",5),2500)

@mcp.tool
def search_prices(query:str):
    """Find current product prices from retailers."""
    return format_results(search(f"{query} price India Flipkart Amazon Croma Reliance Digital",5),2500)

@mcp.tool
def search_reviews(query:str):
    """Find expert and user reviews with pros and cons."""
    return format_results(search(f"{query} expert review user reviews pros cons",5),2500)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternative products."""
    return format_results(search(f"{query} comparison alternatives versus review",5),2200)

@mcp.tool
def search_web(query:str):
    """Find additional relevant web information."""
    return format_results(search(f"{query} latest information",4),1800)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews, demonstrations and comparisons."""
    return format_results(search(f"site:youtube.com {query} review comparison",4),1800)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
