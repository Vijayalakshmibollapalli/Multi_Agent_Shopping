import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

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
        x=f"[SOURCE {i}]\nTitle: {r.get('title','')}\nURL: {r.get('url','')}\nContent: {r.get('content','')[:1800]}"
        if total+len(x)>limit: break
        out.append(x)
        total+=len(x)
    return "\n\n".join(out)

@mcp.tool
def search_products(query:str):
    """Find real products and relevant specifications."""
    return format_data(search(f"{query} products India models specifications features comparison",6),5000)

@mcp.tool
def search_prices(query:str):
    """Find current product prices and availability."""
    return format_data(search(f"{query} India current price Amazon Flipkart Croma Reliance Digital official store",6),4500)

@mcp.tool
def search_reviews(query:str):
    """Find product reviews, pros, cons and user feedback."""
    return format_data(search(f"{query} India expert review user review pros cons problems rating",6),4500)

@mcp.tool
def search_comparison(query:str):
    """Find product comparisons and alternatives."""
    return format_data(search(f"{query} comparison alternatives similar products advantages disadvantages",5),3500)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
