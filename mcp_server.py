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

def format_results(results,limit=1800):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:400]
        if not title or not url: continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_only(results):
    blocked=["youtube.com","youtu.be","reddit.com","91mobiles.com","laptopinsights.in","amazon.","flipkart.com","gadgetsnow.","bajajfinserv.","croma.com"]
    return [x for x in results if not any(site in str(x.get("url","")).lower() for site in blocked)]

@mcp.tool
def search_products(query:str):
    """Find relevant products and models."""
    return format_results(search(f"{query} best products India models",4),1600)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer or brand specifications."""
    results=official_only(search(f"{query} official manufacturer specifications product",5))
    return format_results(results,1800)

@mcp.tool
def search_prices(query:str):
    """Find current product prices."""
    return format_results(search(f"{query} current price India buy",4),1500)

@mcp.tool
def search_reviews(query:str):
    """Find reviews with pros and cons."""
    return format_results(search(f"{query} review pros cons",3),1100)

@mcp.tool
def search_comparison(query:str):
    """Find alternatives and comparisons."""
    return format_results(search(f"{query} comparison alternatives",3),900)

@mcp.tool
def search_web(query:str):
    """Find useful buying guides and web research."""
    return format_results(search(f"{query} buying guide review India",3),800)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube product reviews."""
    return format_results(search(f"site:youtube.com {query} review",2),600)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
