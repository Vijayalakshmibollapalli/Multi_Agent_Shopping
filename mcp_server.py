import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=5):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"Search Error","url":"","content":str(e)}]

def format_results(results,limit=5000):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        content=item.get("content","")[:1200]
        text=f"SOURCE {i}\nTITLE: {item.get('title','')}\nURL: {item.get('url','')}\nCONTENT: {content}\n\n"
        if total+len(text)>limit:
            break
        output.append(text)
        total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):
    """Find relevant product models and product information."""
    return format_results(search(f"{query} best product models features specifications",6),5000)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications."""
    return format_results(search(f"{query} official manufacturer specifications site official",6),4500)

@mcp.tool
def search_prices(query:str):
    """Find current product prices from retailers."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital",6),4500)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews and user feedback."""
    return format_results(search(f"{query} expert review user reviews pros cons problems",6),4500)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternative products."""
    return format_results(search(f"{query} comparison versus alternatives review",5),4000)

@mcp.tool
def search_web(query:str):
    """Find broader relevant web information."""
    return format_results(search(f"{query} latest information review analysis",5),3500)

@mcp.tool
def search_youtube(query:str):
    """Find YouTube product reviews, demonstrations and comparisons."""
    return format_results(search(f"site:youtube.com {query} review comparison demonstration unboxing",5),3000)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
