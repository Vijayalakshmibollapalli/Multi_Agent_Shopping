import os,json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()

mcp=FastMCP(name="AI Shopping Intelligence")

def search_web(query,max_results=5):
    key=os.getenv("TAVILY_API_KEY")
    if not key:
        return [{"title":"ERROR","url":"","content":"TAVILY_API_KEY missing"}]
    try:
        client=TavilyClient(api_key=key)
        r=client.search(query=query,search_depth="advanced",max_results=max_results)
        return r.get("results",[])
    except Exception as e:
        return [{"title":"ERROR","url":"","content":str(e)}]

def clean(data,limit=5000):
    return json.dumps([
        {"title":x.get("title",""),"url":x.get("url",""),"content":x.get("content","")}
        for x in data
    ],ensure_ascii=False)[:limit]

@mcp.tool
def search_products(query:str)->str:
    return clean(search_web(f"{query} best products exact models specifications India 2026",5))

@mcp.tool
def search_prices(query:str)->str:
    return clean(search_web(f"{query} current price India Amazon Flipkart Croma official store 2026",5))

@mcp.tool
def search_reviews(query:str)->str:
    return clean(search_web(f"{query} reviews ratings pros cons customer experience India 2026",5),4000)

@mcp.tool
def search_comparison(query:str)->str:
    return clean(search_web(f"{query} comparison alternatives competing products India 2026",5),4000)

if __name__=="__main__":
    print("Starting AI Shopping Intelligence MCP Server...")
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
