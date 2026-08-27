import os,re
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=6):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def clean_text(text):
    text=re.sub(r"\s+"," ",str(text or "")).strip()
    return text

def clean_url(url):
    url=str(url or "").strip()
    url=url.replace("\\nContent:","").replace("\nContent:","")
    url=re.sub(r"/nContent.*$","",url,flags=re.I)
    url=re.sub(r"\\n.*$","",url)
    return url.strip()

def format_results(results,limit=5000):
    output=[]
    total=0

    for i,item in enumerate(results,1):
        title=clean_text(item.get("title",""))
        url=clean_url(item.get("url",""))
        content=clean_text(item.get("content",""))

        if not title or not url:
            continue

        text=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content[:1000]}\n\n"

        if total+len(text)>limit:
            break

        output.append(text)
        total+=len(text)

    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant real product models for any shopping request."""
    return format_results(search(f"{query} best products models India buy",6),5000)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer or brand product specifications."""
    return format_results(search(f"{query} official specifications manufacturer brand product",6),4500)

@mcp.tool
def search_prices(query:str):
    """Find current prices from official stores and recognized retailers."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital Vijay Sales official store",6),4500)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, pros, cons and known limitations."""
    return format_results(search(f"{query} review pros cons expert review user experience",6),4500)

@mcp.tool
def search_comparison(query:str):
    """Find product comparisons and alternative options."""
    return format_results(search(f"{query} comparison alternatives versus best option",6),4000)

@mcp.tool
def search_web(query:str):
    """Find additional relevant buying guides and product information."""
    return format_results(search(f"{query} buying guide latest information India",6),3500)

@mcp.tool
def search_youtube(query:str):
    """Find relevant YouTube reviews, demonstrations and comparisons."""
    return format_results(search(f"site:youtube.com {query} review comparison unboxing demonstration",5),3000)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
