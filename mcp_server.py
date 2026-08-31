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
        for item in data.get("results",[]):
            results.append({"title":item.get("title",""),"content":item.get("content","")[:600],"url":item.get("url","")})
        return results
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    query=f"{query} India exact product models specifications price"
    return json.dumps(search_web(query,6),ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    query=f'"{product}" specifications features official India'
    return json.dumps(search_web(query,4),ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    query=f'"{product}" price India INR'
    return json.dumps(search_web(query,4),ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    query=f'"{product}" review pros cons'
    return json.dumps(search_web(query,3),ensure_ascii=False)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="127.0.0.1",port=8000)
