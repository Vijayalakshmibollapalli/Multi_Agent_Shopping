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
        return [{"title":x.get("title",""),"content":x.get("content","")[:1500],"url":x.get("url","")} for x in data.get("results",[])]
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    return json.dumps(search_web(f"{query} best products India exact model number specifications price",8),ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    return json.dumps(search_web(f'"{product}" features specifications details',5),ensure_ascii=False)

@mcp.tool
def search_official_specs(product:str)->str:
    return json.dumps(search_web(f'"{product}" official specifications manufacturer',5),ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    return json.dumps(search_web(f'"{product}" price India Amazon Flipkart Croma Reliance Digital Vijay Sales',6),ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    return json.dumps(search_web(f'"{product}" review pros cons performance',5),ensure_ascii=False)

@mcp.tool
def search_comparison(products:str)->str:
    return json.dumps(search_web(f"{products} comparison specifications price review",5),ensure_ascii=False)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT",8000)))
