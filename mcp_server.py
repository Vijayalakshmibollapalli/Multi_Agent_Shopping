import os,json
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
        for x in data.get("results",[]):
            results.append({"title":x.get("title",""),"content":x.get("content","")[:700],"url":x.get("url","")})
        return results
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    search_query=f"{query} India actual product models exact model number laptop price specifications buy"
    return json.dumps(search_web(search_query,8),ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    search_query=f'"{product}" exact model specifications RAM processor storage display'
    return json.dumps(search_web(search_query,4),ensure_ascii=False)

@mcp.tool
def search_official_specs(product:str)->str:
    search_query=f'"{product}" official specifications site:*.com'
    return json.dumps(search_web(search_query,4),ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    search_query=f'"{product}" price India Amazon Flipkart Croma Reliance'
    return json.dumps(search_web(search_query,4),ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    search_query=f'"{product}" review pros cons performance'
    return json.dumps(search_web(search_query,3),ensure_ascii=False)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT",8000)))
