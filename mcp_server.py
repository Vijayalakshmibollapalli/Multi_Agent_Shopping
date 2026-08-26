import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()
mcp=FastMCP("AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=6):
    try:return tavily.search(query=query,max_results=n,search_depth="advanced",include_answer=False).get("results",[])
    except Exception as e:return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=4500):
    output=[];total=0
    for i,item in enumerate(results,1):
        text=f"[SOURCE {i}]\nTITLE: {item.get('title','')}\nURL: {item.get('url','')}\nCONTENT: {item.get('content','')[:1200]}\n\n"
        if total+len(text)>limit:break
        output.append(text);total+=len(text)
    return "".join(output)

@mcp.tool
def search_products(query:str):return format_results(search(f"{query} product models features available products",6),4500)

@mcp.tool
def search_official_specs(query:str):return format_results(search(f"{query} official manufacturer specifications product page",6),4500)

@mcp.tool
def search_prices(query:str):return format_results(search(f"{query} current price India retailer Amazon Flipkart Croma Reliance Digital",6),4500)

@mcp.tool
def search_reviews(query:str):return format_results(search(f"{query} expert reviews user reviews pros cons problems Reddit",6),4500)

@mcp.tool
def search_comparison(query:str):return format_results(search(f"{query} comparison alternatives versus pros cons",6),4000)

@mcp.tool
def search_web(query:str):return format_results(search(f"{query} latest information product research",6),3500)

@mcp.tool
def search_youtube(query:str):return format_results(search(f"site:youtube.com {query} review comparison demonstration unboxing",6),3000)

if __name__=="__main__":mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
