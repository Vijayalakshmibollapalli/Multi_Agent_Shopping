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

def domain(url):
    match=re.search(r"https?://(?:www\.)?([^/]+)",str(url or "").lower())
    return match.group(1) if match else ""

def format_results(results,limit=2500):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:650]
        if not title or not url or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nDomain: {domain(url)}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def official_results(results):
    blocked=["amazon.","flipkart.","croma.","reliancedigital.","gadgets360.","91mobiles.","smartprix.","nanoreview.","facebook.","reddit.","youtube.","hindustantimes."]
    return [item for item in results if not any(x in domain(item.get("url","")) for x in blocked)]

@mcp.tool
def search_products(query:str):
    """Find multiple real product candidates for any shopping request."""
    return format_results(search(f"{query} India best products models buy options",8),3200)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or brand specification pages for an exact product."""
    results=official_results(search(f"{query} official specifications manufacturer product specs",8))
    return format_results(results,3000)

@mcp.tool
def search_prices(query:str):
    """Find current product prices from India retailers and price sources."""
    return format_results(search(f"{query} current price India buy price",8),3000)

@mcp.tool
def search_reviews(query:str):
    """Find independent reviews, pros, cons and user experience."""
    return format_results(search(f"{query} review pros cons performance problems",6),2400)

@mcp.tool
def search_comparison(query:str):
    """Find comparable alternatives and product comparisons."""
    return format_results(search(f"{query} alternatives competitors comparison",6),2200)

@mcp.tool
def search_web(query:str):
    """Find additional reliable information relevant to purchase decisions."""
    return format_results(search(f"{query} buying guide features value for money",5),1800)

@mcp.tool
def search_youtube(query:str):
    """Find video review links for a product."""
    return format_results(search(f"site:youtube.com {query} review",5),1400)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
