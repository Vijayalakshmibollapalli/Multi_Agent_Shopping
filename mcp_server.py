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
    except Exception: return []

def format_results(results,limit=1800,content_limit=300):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url",""))
        content=clean(item.get("content",""))[:content_limit]
        if not title or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_results(results):
    blocked=["youtube.com","youtu.be","reddit.com","facebook.com","instagram.com"]
    return [item for item in results if not any(site in item.get("url","").lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find real product models matching the user's shopping request."""
    results=search(f"{query} laptop phone product models India specifications price",6)
    return format_results(results,1800,260)

@mcp.tool
def search_candidate_details(query:str):
    """Find exact specifications for a product model."""
    results=search(f'"{query}" exact model specifications',4)
    return format_results(results,1300,280)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    results=official_results(search(f'"{query}" official specifications manufacturer',5))
    return format_results(results,1400,280)

@mcp.tool
def search_prices(query:str):
    """Find current price in India for an exact product."""
    results=search(f'"{query}" price India',5)
    return format_results(results,1300,240)

@mcp.tool
def search_reviews(query:str):
    """Find reviews for an exact product model."""
    results=search(f'"{query}" review pros cons',4)
    return format_results(results,1000,220)

@mcp.tool
def search_comparison(query:str):
    """Find alternatives and comparisons for a product."""
    results=search(f'"{query}" alternatives comparison',4)
    return format_results(results,1000,220)

@mcp.tool
def search_web(query:str):
    """Find additional product information."""
    results=search(f'"{query}" specifications features',4)
    return format_results(results,900,200)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews."""
    results=search(f'site:youtube.com "{query}" review',3)
    return format_results(results,700,180)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
