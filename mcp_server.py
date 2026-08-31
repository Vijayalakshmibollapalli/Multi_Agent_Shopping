import os,json
from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp=FastMCP(name="AI Shopping Intelligence MCP Server")
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query,max_results=5):
    try:
        response=tavily.search(query=query,search_depth="advanced",max_results=max_results,include_answer=False,include_raw_content=False)
        results=[]
        for item in response.get("results",[]):
            title=str(item.get("title","")).strip()
            content=str(item.get("content","")).strip()
            url=str(item.get("url","")).strip()
            if title or content:
                results.append({"title":title,"content":content[:1400],"url":url})
        return results
    except Exception as e:
        return [{"error":str(e)}]

@mcp.tool
def search_products(query:str)->str:
    searches=[f"{query} India exact product models price specifications",f"{query} India laptops products models current price",f"{query} India best products exact model"]
    combined=[]
    seen=set()
    for q in searches:
        for item in search_web(q,6):
            key=(item.get("title",""),item.get("url",""))
            if key not in seen:
                seen.add(key)
                combined.append(item)
    return json.dumps(combined[:15],ensure_ascii=False)

@mcp.tool
def search_product_details(product:str)->str:
    queries=[f'"{product}" specifications India',f'"{product}" features processor RAM storage display',f'"{product}" official specifications']
    combined=[]
    seen=set()
    for q in queries:
        for item in search_web(q,5):
            key=(item.get("title",""),item.get("url",""))
            if key not in seen:
                seen.add(key)
                combined.append(item)
    return json.dumps(combined[:12],ensure_ascii=False)

@mcp.tool
def search_prices(product:str)->str:
    queries=[f'"{product}" price India INR',f'"{product}" current price India',f'"{product}" Amazon Flipkart price India']
    combined=[]
    seen=set()
    for q in queries:
        for item in search_web(q,5):
            key=(item.get("title",""),item.get("url",""))
            if key not in seen:
                seen.add(key)
                combined.append(item)
    return json.dumps(combined[:12],ensure_ascii=False)

@mcp.tool
def search_reviews(product:str)->str:
    queries=[f'"{product}" review pros cons India',f'"{product}" user reviews performance battery',f'"{product}" review']
    combined=[]
    seen=set()
    for q in queries:
        for item in search_web(q,5):
            key=(item.get("title",""),item.get("url",""))
            if key not in seen:
                seen.add(key)
                combined.append(item)
    return json.dumps(combined[:12],ensure_ascii=False)

if __name__=="__main__":
    port=int(os.getenv("PORT","8000"))
    mcp.run(transport="streamable-http",host="0.0.0.0",port=port)
