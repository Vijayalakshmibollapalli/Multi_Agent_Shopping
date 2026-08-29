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

def format_results(results,limit=2200):
    output=[];total=0
    for i,item in enumerate(results,1):
        title=clean(item.get("title",""));url=clean(item.get("url","")).replace("\\n","").replace("\n","");content=clean(item.get("content",""))[:550]
        if not title or not url or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def remove_domains(results,domains):
    return [x for x in results if not any(domain in str(x.get("url","")).lower() for domain in domains)]

def official_search(query,n=6):
    results=search(query,n)
    blocked=["amazon.","flipkart.","youtube.","youtu.be","reddit.","facebook.","instagram.","91mobiles.","gadgetsnow.","cashify.","pricehistory."]
    return remove_domains(results,blocked)

@mcp.tool
def search_products(query:str):
    """Find multiple real products and exact models relevant to any shopping request."""
    results=search(f"{query} India best models current price specifications alternatives",8)
    return format_results(results,3000)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or official brand specifications for an exact product model."""
    results=official_search(f"{query} official specifications manufacturer brand product",7)
    return format_results(results,2600)

@mcp.tool
def search_prices(query:str):
    """Find current India prices from reliable stores and product listings."""
    results=search(f"{query} current price India buy price ₹",7)
    return format_results(results,2400)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, pros, cons and real-world product analysis."""
    results=search(f"{query} review pros cons performance drawbacks India",6)
    return format_results(results,2000)

@mcp.tool
def search_comparison(query:str):
    """Find competing products, alternatives and comparison information."""
    results=search(f"{query} alternatives competitors comparison better options India",6)
    return format_results(results,2000)

@mcp.tool
def search_web(query:str):
    """Find additional reliable research about the product."""
    results=search(f"{query} specifications features performance buying guide",5)
    return format_results(results,1600)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube video reviews for the product."""
    results=search(f"site:youtube.com {query} review unboxing",4)
    return format_results(results,1000)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
