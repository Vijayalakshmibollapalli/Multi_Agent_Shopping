import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP
load_dotenv()
mcp=FastMCP(name="AI Shopping Intelligence")
def safe_search(query,max_results=6):
    key=os.getenv("TAVILY_API_KEY")
    if not key:return [{"title":"ERROR","url":"","content":"TAVILY_API_KEY is missing"}]
    try:return TavilyClient(api_key=key).search(query=query,search_depth="advanced",max_results=max_results,include_answer=False).get("results",[])
    except Exception as e:return [{"title":"TAVILY_ERROR","url":"","content":str(e)}]
def clean_results(results):
    return json.dumps([{"title":str(x.get("title","")).strip()[:300],"url":str(x.get("url","")).strip(),"content":str(x.get("content","")).strip()[:2500]} for x in results[:6]],ensure_ascii=False)
@mcp.tool
def search_products(query:str)->str:return clean_results(safe_search(f"{query} best products exact models specifications features India current 2026",6))
@mcp.tool
def search_prices(query:str)->str:return clean_results(safe_search(f"{query} current price India 2026 Amazon Flipkart Croma Reliance Digital official store price",6))
@mcp.tool
def search_reviews(query:str)->str:return clean_results(safe_search(f"{query} reviews ratings pros cons performance customer experience India 2026",6))
@mcp.tool
def search_comparison(query:str)->str:return clean_results(safe_search(f"{query} comparison alternatives competing products best value India 2026",6))
if __name__=="__main__":print("Starting AI Shopping Intelligence MCP Server...");mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
