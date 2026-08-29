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

def filter_sources(results,blocked=None):
    blocked=blocked or []
    output=[]
    for item in results:
        url=str(item.get("url","")).lower()
        if not any(site in url for site in blocked): output.append(item)
    return output

@mcp.tool
def search_products(query:str):
    """Find multiple real product names and models relevant to any shopping request."""
    results=search(f"{query} best products models India specifications price",6)
    return format_results(results,2800)

@mcp.tool
def verify_product(query:str):
    """Verify whether an exact product name or model exists and find reliable product information."""
    results=search(f'"{query}" specifications model product',6)
    return format_results(results,2600)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or brand specifications for an exact product model."""
    results=search(f'"{query}" official specifications manufacturer brand',6)
    results=filter_sources(results,["youtube.com","youtu.be","reddit.com","facebook.com","instagram.com"])
    return format_results(results,2400)

@mcp.tool
def search_prices(query:str):
    """Find current product prices and sellers in India."""
    results=search(f'"{query}" price India buy current price',6)
    return format_results(results,2200)

@mcp.tool
def search_reviews(query:str):
    """Find independent reviews with advantages, disadvantages and real-world usage."""
    results=search(f'"{query}" review pros cons performance',5)
    return format_results(results,1800)

@mcp.tool
def search_comparison(query:str):
    """Find comparable alternative products and comparisons."""
    results=search(f'"{query}" alternatives comparison similar products',5)
    return format_results(results,1600)

@mcp.tool
def search_web(query:str):
    """Find additional reliable buying information for any product."""
    results=search(f'"{query}" buying guide specifications review',4)
    return format_results(results,1400)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews for an exact product."""
    results=search(f'site:youtube.com "{query}" review',3)
    return format_results(results,900)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
