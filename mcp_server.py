import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(text): return re.sub(r"\s+"," ",str(text or "")).strip()

def search(query,n=5):
    try: return tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False).get("results",[])
    except Exception as e: return []

def format_results(results,limit=1600,content_limit=300):
    output=[];total=0
    for item in results:
        title=clean(item.get("title",""))
        url=clean(item.get("url",""))
        content=clean(item.get("content",""))[:content_limit]
        if not title or not url.startswith("http"): continue
        text=f"Title: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find real products relevant to the user's shopping request."""
    return format_results(search(f"{query} exact laptop models India",6),1800,280)

@mcp.tool
def search_candidate_details(query:str):
    """Find specifications for one exact product model."""
    return format_results(search(f'"{query}" specifications model',4),1200,280)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return format_results(search(f'"{query}" official specifications manufacturer',4),1200,280)

@mcp.tool
def search_prices(query:str):
    """Find current India prices for an exact product."""
    return format_results(search(f'"{query}" price India',5),1200,250)

@mcp.tool
def search_reviews(query:str):
    """Find reviews and user feedback."""
    return format_results(search(f'"{query}" review pros cons',4),1000,240)

@mcp.tool
def search_comparison(query:str):
    """Find similar competing products."""
    return format_results(search(f'"{query}" alternatives comparison',4),1000,220)

@mcp.tool
def search_web(query:str):
    """Find additional reliable product information."""
    return format_results(search(f'"{query}" features specifications',3),800,220)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews."""
    return format_results(search(f'site:youtube.com "{query}" review',3),700,180)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
