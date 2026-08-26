import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient
from langchain_community.tools import DuckDuckGoSearchResults,YouTubeSearchTool

load_dotenv()

mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
duckduckgo=DuckDuckGoSearchResults(output_format="list",num_results=6)
youtube=YouTubeSearchTool()

def tavily_search(query,n=6):
    try:
        return tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
    except Exception as e:
        return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=5000):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        text=f"[SOURCE {i}]\nTitle: {item.get('title','')}\nURL: {item.get('url','')}\nContent: {item.get('content','')[:1500]}\n"
        if total+len(text)>limit: break
        output.append(text)
        total+=len(text)
    return "\n".join(output)

@mcp.tool
def search_products(query:str):
    """Find real product models, features and specifications from web sources."""
    results=tavily_search(f"{query} product models specifications features official website",6)
    return format_results(results,5000)

@mcp.tool
def search_official_specs(query:str):
    """Find official manufacturer specifications and product information."""
    results=tavily_search(f"{query} official product specifications manufacturer website",5)
    return format_results(results,4500)

@mcp.tool
def search_prices(query:str):
    """Find current prices and availability from Indian retailers and official stores."""
    results=tavily_search(f"{query} current price India Amazon Flipkart Croma Reliance Digital official store",6)
    return format_results(results,4500)

@mcp.tool
def search_reviews(query:str):
    """Find expert reviews, user feedback, pros, cons and common problems."""
    results=tavily_search(f"{query} expert review user review pros cons problems Reddit",6)
    return format_results(results,4500)

@mcp.tool
def search_comparison(query:str):
    """Find comparisons, alternatives and differences between relevant products."""
    results=tavily_search(f"{query} comparison alternatives vs advantages disadvantages",5)
    return format_results(results,4000)

@mcp.tool
def search_web(query:str):
    """Search additional web sources using DuckDuckGo."""
    try:
        results=duckduckgo.invoke(query)
        return str(results)[:4000]
    except Exception as e:
        return f"Web search error: {str(e)}"

@mcp.tool
def search_youtube(query:str):
    """Find YouTube videos such as product reviews, comparisons and demonstrations."""
    try:
        results=youtube.invoke(f"{query} review comparison,5")
        return str(results)[:3000]
    except Exception as e:
        return f"YouTube search error: {str(e)}"

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)