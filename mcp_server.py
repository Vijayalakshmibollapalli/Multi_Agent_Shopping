import os
from dotenv import load_dotenv
from tavily import TavilyClient
from fastmcp import FastMCP

load_dotenv()
mcp = FastMCP("AI Shopping Intelligence MCP Server")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query,n=5):
    try:
        result=tavily.search(query=query,max_results=n,search_depth="basic",include_answer=False)
        return result.get("results",[])
    except Exception as e:
        return [{"title":"SEARCH_ERROR","url":"","content":str(e)}]

def format_results(results,limit=6000):
    output=[]
    total=0
    for i,item in enumerate(results,1):
        text=f"[SOURCE {i}]\nTitle: {item.get('title','')}\nURL: {item.get('url','')}\nContent: {item.get('content','')[:1200]}"
        if total+len(text)>limit:
            break
        output.append(text)
        total+=len(text)
    return "\n\n".join(output)

@mcp.tool
def search_products(query:str)->str:
    """Find real products matching the user's shopping requirements."""
    return format_results(search(f"{query} real products India models specifications features",5),5000)

@mcp.tool
def search_prices(query:str)->str:
    """Find current prices and availability for products in India."""
    return format_results(search(f"{query} current price India Amazon Flipkart Croma Reliance Digital official store",5),4500)

@mcp.tool
def search_reviews(query:str)->str:
    """Find product reviews, pros, cons and customer feedback."""
    return format_results(search(f"{query} reviews pros cons user feedback India problems",5),4500)

@mcp.tool
def search_comparison(query:str)->str:
    """Find comparisons and alternative products."""
    return format_results(search(f"{query} comparison alternatives similar products advantages disadvantages",4),3500)

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="127.0.0.1",port=8000)
