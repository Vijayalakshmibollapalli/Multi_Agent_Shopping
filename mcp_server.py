import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(text): return re.sub(r"\s+"," ",str(text or "")).strip()

def search(query,n=4):
    try: return tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False).get("results",[])
    except Exception as e: return []

def format_results(results,limit=1200,content_limit=250):
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

def official_results(results):
    blocked=["amazon.","flipkart.","reddit.com","youtube.com","facebook.com","instagram.com","pricehistory."]
    return [x for x in results if not any(site in x.get("url","").lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find specific product models matching the user's request."""
    results=search(f"{query} exact model price specifications India",5)
    return format_results(results,1400,220)

@mcp.tool
def search_specs(query:str):
    """Find specifications for an exact product model."""
    results=official_results(search(f'"{query}" official specifications',4))
    if not results: results=search(f'"{query}" specifications processor RAM storage display',4)
    return format_results(results,1100,220)

@mcp.tool
def search_prices(query:str):
    """Find current price information in India."""
    results=search(f'"{query}" price India',4)
    return format_results(results,900,180)

@mcp.tool
def search_reviews(query:str):
    """Find reliable reviews and practical pros and cons."""
    results=search(f'"{query}" review pros cons',3)
    return format_results(results,800,180)

@mcp.tool
def search_alternatives(query:str):
    """Find similar alternative products."""
    results=search(f'"{query}" alternatives similar products India',3)
    return format_results(results,800,180)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
