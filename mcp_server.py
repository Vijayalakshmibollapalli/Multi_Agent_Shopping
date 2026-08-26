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

def format_results(results,limit=5000):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        content=item.get("content","")
        text=f"[SOURCE {i}]\nTitle: {item.get('title','')}\nURL: {item.get('url','')}\nContent: {content[:1200]}\n"
        if total+len(text)>limit:
            break
        output.append(text)
        total+=len(text)
    return "\n".join(output)

@mcp.tool
def search_products(query:str):
    """Find real product models relevant to the user's request."""
    return format_results(search(f"{query} best product models available India",6),5000)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer and official brand specifications."""
    return format_results(search(f"{query} official manufacturer specifications site:*.com product specifications",6),4500)

@mcp.tool
def search_prices(query:str):
    """Find current prices from retailers and official stores."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital official store",6),4500)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, advantages and limitations."""
    return format_results(search(f"{query} expert review user review pros cons problems",6),4500)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons between relevant products and alternatives."""
    return format_results(search(f"{query} comparison versus alternatives pros cons",6),4000)

@mcp.tool
def search_web(query:str):
    """Find additional relevant information from the web."""
    return format_results(search(f"{query} latest information buying guide",6),3500)

@mcp.tool
def search_youtube(query:str):
    """Find relevant YouTube reviews, demonstrations and comparisons."""
    return format_results(search(f"site:youtube.com {query} review comparison demonstration unboxing",6),3000)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
