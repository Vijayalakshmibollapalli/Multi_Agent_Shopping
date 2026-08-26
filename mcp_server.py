import os
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

def format_results(results,limit=4500):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        title=item.get("title","")
        url=item.get("url","")
        content=item.get("content","")
        text=f"SOURCE {i}\nTITLE: {title}\nURL: {url}\nCONTENT: {content[:1200]}\n\n"
        if total+len(text)>limit: break
        output.append(text)
        total+=len(text)
    return "".join(output) if output else "No verified results found."

@mcp.tool
def search_products(query:str):
    """Find relevant real product models and product information."""
    return format_results(search(f"{query} best product models specifications",6),4000)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer product specifications."""
    return format_results(search(f"{query} official manufacturer specifications site:asus.com OR site:hp.com OR site:dell.com OR site:lenovo.com OR site:acer.com OR site:msi.com",6),4000)

@mcp.tool
def search_prices(query:str):
    """Find current product prices from shopping and retailer sources."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital",6),4000)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user experiences, pros and cons."""
    return format_results(search(f"{query} review pros cons user experience expert review",6),4000)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons and alternative products."""
    return format_results(search(f"{query} comparison versus alternatives",6),3500)

@mcp.tool
def search_web(query:str):
    """Find broader web research relevant to the product decision."""
    return format_results(search(f"{query} programming review buying guide latest",6),3000)

@mcp.tool
def search_youtube(query:str):
    """Find relevant YouTube product review and comparison videos."""
    return format_results(search(f"site:youtube.com/watch {query} review comparison",6),2500)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
