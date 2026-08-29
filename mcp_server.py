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

def format_results(results,limit=1800,content_limit=300):
    output=[];total=0
    for item in results:
        title=clean(item.get("title",""))
        url=clean(item.get("url",""))
        content=clean(item.get("content",""))[:content_limit]
        if not title or not valid_url(url): continue
        text=f"Title: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find exact purchasable product models for the user's shopping request."""
    return format_results(search(f"{query} exact model specifications price India",8),2200,280)

@mcp.tool
def search_product_details(query:str):
    """Find exact specifications for one specific product model."""
    return format_results(search(f'"{query}" exact specifications RAM processor storage India',6),1800,300)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications for one exact product model."""
    return format_results(search(f'"{query}" official specifications manufacturer',6),1800,300)

@mcp.tool
def search_prices(query:str):
    """Find current India price for one exact product model."""
    return format_results(search(f'"{query}" price India buy ₹',6),1600,260)

@mcp.tool
def search_reviews(query:str):
    """Find reviews for one exact product model."""
    return format_results(search(f'"{query}" review pros cons',5),1400,260)

@mcp.tool
def search_alternatives(query:str):
    """Find competing exact product models."""
    return format_results(search(f"{query} best alternatives similar price India",5),1400,240)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
