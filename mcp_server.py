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
        title=clean(item.get("title",""))
        url=clean(item.get("url","")).replace("\\n","").replace("\n","")
        content=clean(item.get("content",""))[:650]
        if not title or not url or not url.startswith("http"): continue
        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
        if total+len(text)>limit: break
        output.append(text);total+=len(text)
    return "".join(output)

def remove_domains(results,domains):
    return [x for x in results if not any(domain in clean(x.get("url","")).lower() for domain in domains)]

def official_results(results):
    blocked=["reddit.com","youtube.com","youtu.be","facebook.com","instagram.com","twitter.com","x.com"]
    return remove_domains(results,blocked)

@mcp.tool
def search_products(query:str):
    """Find multiple real products and exact models matching any shopping request, purpose, requirements and budget."""
    results=search(f"{query} India best options exact model price specifications",8)
    return format_results(results,3200)

@mcp.tool
def search_product_details(query:str):
    """Find exact specifications and configuration details for a product model."""
    results=search(f"{query} specifications exact model configuration features",6)
    return format_results(results,2600)

@mcp.tool
def search_official_specs(query:str):
    """Find manufacturer or official product specifications. Prefer official sources but return reliable sources when official data is unavailable."""
    results=official_results(search(f"{query} official specifications manufacturer product",7))
    return format_results(results,2400)

@mcp.tool
def search_prices(query:str):
    """Find current product prices and available listings in India."""
    results=search(f"{query} current price India buy price ₹",7)
    return format_results(results,2200)

@mcp.tool
def search_reviews(query:str):
    """Find reliable reviews, pros, cons and real-world product performance."""
    results=search(f"{query} review pros cons performance",6)
    return format_results(results,2000)

@mcp.tool
def search_comparison(query:str):
    """Find comparable alternatives and competing products."""
    results=search(f"{query} alternatives competitors comparison India",6)
    return format_results(results,1800)

@mcp.tool
def search_web(query:str):
    """Find additional reliable information relevant to the purchase decision."""
    results=search(f"{query} buying guide features comparison India",5)
    return format_results(results,1600)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube product reviews and hands-on videos."""
    results=search(f"site:youtube.com {query} review hands on",4)
    return format_results(results,1200)

if __name__=="__main__": mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT","8000")))
