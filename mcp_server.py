import os,json
from tavily import TavilyClient
from fastmcp import FastMCP

mcp=FastMCP(name="AI Shopping Intelligence")

def search_web(query:str,max_results:int=5)->list:
    api_key=os.getenv("TAVILY_API_KEY")
    if not api_key:return [{"title":"TAVILY_API_KEY_ERROR","url":"","content":"TAVILY_API_KEY is missing on the MCP server."}]
    try:
        client=TavilyClient(api_key=api_key)
        result=client.search(query=query,search_depth="advanced",max_results=max_results,include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"TAVILY_ERROR","url":"","content":str(e)}]

def clean_result(item):
    return {"title":str(item.get("title","")).strip(),"url":str(item.get("url","")).strip(),"content":str(item.get("content","")).strip()}

def compact_results(results:list,limit:int=7000)->str:
    cleaned=[clean_result(x) for x in results]
    return json.dumps(cleaned,ensure_ascii=False)[:limit]

@mcp.tool
def search_products(query:str)->str:
    return compact_results(search_web(f"{query} specific product models best products specifications features India 2026",5),7000)

@mcp.tool
def search_prices(query:str)->str:
    return compact_results(search_web(f"{query} specific product model current price India 2026 Amazon Flipkart Croma official store",5),7000)

@mcp.tool
def search_reviews(query:str)->str:
    return compact_results(search_web(f"{query} specific product models reviews ratings pros cons user experience India 2026",5),6000)

@mcp.tool
def search_comparison(query:str)->str:
    return compact_results(search_web(f"{query} specific product models comparison alternatives competitors India 2026",5),6000)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8000)
