import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()
mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=5):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"Search unavailable","url":"","content":str(e)}]

def format_results(results,limit=3500):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        title=item.get("title","Unknown source")
        url=item.get("url","")
        content=item.get("content","")[:700]
        text=f"[SOURCE {i}]\nTITLE: {title}\nURL: {url}\nCONTENT: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text)
        total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant product models and available options."""
    return format_results(search(f"{query} best product models available options",5))

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return format_results(search(f"{query} official manufacturer specifications site:*.com",5))

@mcp.tool
def search_prices(query:str):
    """Find current retailer price information."""
    return format_results(search(f"{query} current price India Flipkart Amazon Croma Reliance Digital",5))

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, pros and cons."""
    return format_results(search(f"{query} expert review user review pros cons problems",5))

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternative products."""
    return format_results(search(f"{query} comparison alternatives vs review",5))

@mcp.tool
def search_web(query:str):
    """Find relevant web research."""
    return format_results(search(f"{query} latest information buying guide review",5))

@mcp.tool
def search_youtube(query:str):
    """Find relevant YouTube reviews and demonstrations."""
    return format_results(search(f"site:youtube.com/watch {query} review comparison unboxing",5))

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
