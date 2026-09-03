import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is missing in .env")

tavily=TavilyClient(api_key=TAVILY_API_KEY)

def search(query,n=6):
    try:
        r=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return r.get("results",[])
    except Exception as e:
        return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_data(results,limit=5000):
    out=[]
    total=0
    for i,r in enumerate(results,1):
        if not isinstance(r,dict):
            continue
        title=str(r.get("title","")).strip()
        url=str(r.get("url","")).strip()
        content=str(r.get("content","")).strip()
        content=content[:1800]
        x=f"[SOURCE {i}]\nTitle: {title}\nURL: {url}\nContent: {content}"
        if total+len(x)>limit:
            break
        out.append(x)
        total+=len(x)
    return "\n\n".join(out)

@mcp.tool
def search_products(query:str):
    """Find real products and relevant specifications for any shopping category."""
    return format_data(search(f"{query} India real products exact model names specifications features variants",6),5000)

@mcp.tool
def search_prices(query:str):
    """Find current product prices and availability in India."""
    return format_data(search(f"{query} India current price price range availability Amazon Flipkart Croma Reliance Digital official store",6),4500)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews user reviews ratings pros cons problems and reliability."""
    return format_data(search(f"{query} India expert reviews user reviews ratings pros cons problems reliability performance",6),4500)

@mcp.tool
def search_comparison(query:str):
    """Find competitors alternatives comparisons specifications prices advantages and disadvantages."""
    return format_data(search(f"{query} India comparison alternatives competitors similar products specifications price advantages disadvantages",6),4000)

if __name__=="__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
