import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=4):
    try: return tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False).get("results",[])
    except Exception as e: return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def clean(text):
    return re.sub(r"\s+"," ",str(text or "")).strip()

def format_results(results,limit=2200):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).split("\\n")[0]
        content=clean(item.get("content",""))[:500]
        if not title or not url: continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text)
        total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant products and models."""
    return format_results(search(f"{query} best products India",4),1800)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return format_results(search(f"{query} official product specifications manufacturer",4),2000)

@mcp.tool
def search_prices(query:str):
    """Find current prices from reliable retailers."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital",4),1800)

@mcp.tool
def search_reviews(query:str):
    """Find reviews, pros and cons."""
    return format_results(search(f"{query} review pros cons",3),1400)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternatives."""
    return format_results(search(f"{query} comparison alternatives",3),1200)

@mcp.tool
def search_web(query:str):
    """Find useful web research."""
    return format_results(search(f"{query} buying guide India",3),1000)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews."""
    return format_results(search(f"site:youtube.com {query} review",2),800)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
