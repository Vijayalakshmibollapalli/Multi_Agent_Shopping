import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()

def search(query,n=5):
    try: return tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
    except Exception as e: return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def clean_url(url):
    url=clean(url).replace("\\n","").replace("\n","")
    url=re.sub(r"(?:/)?(?:n)?Content:?$","",url,flags=re.I)
    return url.rstrip(".,:;)]}")

def format_results(results,limit=2200):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""))
        url=clean_url(item.get("url",""))
        content=clean(item.get("content",""))[:550]
        if not title or not url or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def remove_domains(results,domains):
    output=[]
    for item in results:
        url=clean(item.get("url","")).lower()
        if not any(domain in url for domain in domains): output.append(item)
    return output

@mcp.tool
def search_products(query:str):
    """Find real purchasable products, exact product names, models and variants relevant to any shopping request."""
    results=search(f"{query} best products India exact model price",8)
    return format_results(results,3000)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or official brand specifications for an exact product model."""
    results=search(f"{query} official specifications manufacturer",7)
    blocked=["reddit.com","youtube.com","youtu.be","facebook.com"]
    results=remove_domains(results,blocked)
    return format_results(results,2600)

@mcp.tool
def search_prices(query:str):
    """Find current India prices from reliable stores, brand stores and price comparison sources."""
    results=search(f"{query} price India buy current price",7)
    return format_results(results,2400)

@mcp.tool
def search_reviews(query:str):
    """Find reliable expert reviews, user reviews, pros, cons and real-world experience."""
    results=search(f"{query} review pros cons performance",6)
    return format_results(results,2000)

@mcp.tool
def search_comparison(query:str):
    """Find real competing products, alternatives and comparison information."""
    results=search(f"{query} alternatives competitors comparison India",6)
    return format_results(results,1800)

@mcp.tool
def search_web(query:str):
    """Find additional reliable web research relevant to a purchase decision."""
    results=search(f"{query} specifications buying guide reliability",5)
    return format_results(results,1500)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube reviews for a product."""
    results=search(f"site:youtube.com {query} review",4)
    return format_results(results,1000)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
