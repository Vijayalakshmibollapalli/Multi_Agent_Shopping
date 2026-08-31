import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP(name="AI Shopping Intelligence MCP Server")

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query,max_results=5):
    try:
        data=tavily.search(query=query,search_depth="advanced",max_results=max_results)
        results=[]

        for item in data.get("results",[]):
            results.append({
                "title":item.get("title",""),
                "content":item.get("content","")[:600],
                "url":item.get("url","")
            })

        return results

    except Exception as e:
        return [{"error":str(e)}]


@mcp.tool
def search_products(query:str)->str:
    search_query=f"{query} India exact product model price specifications shopping"
    return json.dumps(search_web(search_query,6),ensure_ascii=False)


@mcp.tool
def search_product_details(product:str)->str:
    search_query=f'"{product}" specifications features exact model'
    return json.dumps(search_web(search_query,4),ensure_ascii=False)


@mcp.tool
def search_prices(product:str)->str:
    search_query=f'"{product}" price India INR buy'
    return json.dumps(search_web(search_query,4),ensure_ascii=False)


@mcp.tool
def search_reviews(product:str)->str:
    search_query=f'"{product}" review pros cons'
    return json.dumps(search_web(search_query,3),ensure_ascii=False)


if __name__=="__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT",8000))
    )
