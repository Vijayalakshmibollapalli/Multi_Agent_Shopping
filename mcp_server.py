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
    except Exception as e: return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=1400,content_limit=280):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:content_limit]
        if not title or not url or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_only(results):
    blocked=["youtube.com","youtu.be","reddit.com","facebook.com","instagram.com","amazon.","flipkart.com","91mobiles.com","gadgetsnow.","pricehistory."]
    return [x for x in results if not any(site in str(x.get("url","")).lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find real product models relevant to any shopping request."""
    return format_results(search(f"{query} best products India models",5),1600,250)

@mcp.tool
def search_candidate_details(query:str):
    """Research exact candidate product identity and configuration."""
    return format_results(search(f'"{query}" exact model specifications configuration',4),1200,260)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or official product specifications."""
    results=official_only(search(f'"{query}" official manufacturer specifications',5))
    return format_results(results,1400,280)

@mcp.tool
def search_prices(query:str):
    """Find current India prices for an exact product model."""
    return format_results(search(f'"{query}" current price India buy',5),1300,240)

@mcp.tool
def search_reviews(query:str):
    """Find reviews with advantages, disadvantages and practical feedback."""
    return format_results(search(f'"{query}" review pros cons',4),1100,240)

@mcp.tool
def search_comparison(query:str):
    """Find comparable alternatives and competing products."""
    return format_results(search(f'"{query}" alternatives comparison India',4),1100,230)

@mcp.tool
def search_web(query:str):
    """Find additional reliable information about the product."""
    return format_results(search(f'"{query}" specifications features buying review',4),1000,220)

@mcp.tool
def search_youtube(query:str):
    """Find video reviews for the exact product."""
    return format_results(search(f'site:youtube.com "{query}" review',3),700,180)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
