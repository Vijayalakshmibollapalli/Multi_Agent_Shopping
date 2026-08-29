import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(text): return re.sub(r"\s+"," ",str(text or "")).strip()

def search(query,n=5):
    try: return tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
    except Exception as e: return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=2200):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:500]
        if not title or not url: continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_results(results):
    blocked=["youtube.com","youtu.be","reddit.com","facebook.com","instagram.com","twitter.com","x.com"]
    return [item for item in results if not any(site in str(item.get("url","")).lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find multiple real product models relevant to any shopping request."""
    return format_results(search(f"{query} best products models India options comparison",7),3200)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications for an exact product model."""
    results=official_results(search(f"{query} official manufacturer specifications model",6))
    return format_results(results,2600)

@mcp.tool
def search_prices(query:str):
    """Find current prices and availability for an exact product."""
    return format_results(search(f"{query} current price India buy price",6),2200)

@mcp.tool
def search_reviews(query:str):
    """Find independent reviews with advantages and disadvantages."""
    return format_results(search(f"{query} review pros cons performance",5),1800)

@mcp.tool
def search_comparison(query:str):
    """Find competing products, alternatives and comparisons."""
    return format_results(search(f"{query} alternatives competitors comparison",5),1600)

@mcp.tool
def search_web(query:str):
    """Find additional reliable product research and buying information."""
    return format_results(search(f"{query} buying guide expert review India",4),1300)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews and hands-on videos."""
    return format_results(search(f"site:youtube.com {query} review hands on",3),900)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
