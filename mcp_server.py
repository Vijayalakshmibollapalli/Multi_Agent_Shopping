import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()

def search(query,n=5):
    try: return tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False).get("results",[])
    except Exception: return []

def valid_url(url):
    url=clean(url).replace("\\n","").replace("\n","")
    return url.startswith("http://") or url.startswith("https://")

def format_results(results,limit=1600,content_limit=260):
    output=[];total=0
    for item in results:
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:content_limit]
        if not title or not valid_url(url) or len(url)<12: continue
        text=f"Title: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_results(results):
    blocked=["reddit.com","facebook.com","instagram.com","youtube.com","youtu.be","91mobiles.com","gadgets360.com","pricehistory.","nanoreview.net"]
    return [x for x in results if valid_url(x.get("url","")) and not any(site in clean(x.get("url","")).lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find exact product models relevant to the user's shopping request."""
    return format_results(search(f"{query} exact product models India",6),1800,220)

@mcp.tool
def search_candidate_details(query:str):
    """Find exact model details for a specific product."""
    return format_results(search(f'"{query}" exact model specifications laptop India',4),1200,240)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications for the exact product."""
    results=official_results(search(f'"{query}" official specifications manufacturer',6))
    return format_results(results,1500,260)

@mcp.tool
def search_prices(query:str):
    """Find current price for an exact product model in India."""
    return format_results(search(f'"{query}" price India exact model',5),1200,220)

@mcp.tool
def search_reviews(query:str):
    """Find reviews for the exact product model."""
    return format_results(search(f'"{query}" exact review pros cons',4),1000,220)

@mcp.tool
def search_comparison(query:str):
    """Find competing product models for comparison."""
    return format_results(search(f'"{query}" alternatives comparison',4),1000,200)

@mcp.tool
def search_web(query:str):
    """Find additional reliable information about the exact product."""
    return format_results(search(f'"{query}" features specifications India',4),900,200)

@mcp.tool
def search_youtube(query:str):
    """Find video reviews for the exact product."""
    return format_results(search(f'site:youtube.com "{query}" review',3),700,160)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
