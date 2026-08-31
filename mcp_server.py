import os,json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP(name="AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query,max_results=3):
    try:
        data=tavily.search(query=query,search_depth="basic",max_results=max_results)
        results=[]
        for item in data.get("results",[])[:max_results]:
            results.append({"title":item.get("title","")[:180],"content":item.get("content","")[:450],"url":item.get("url","")})
        return results
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    return json.dumps(search_web(f"real purchasable products for {query} India price specifications",3),ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    return json.dumps(search_web(f'"{product}" specifications processor RAM storage display India',3),ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    return json.dumps(search_web(f'"{product}" price India INR current',3),ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    return json.dumps(search_web(f'"{product}" review pros cons performance',3),ensure_ascii=False)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT",8000)))
