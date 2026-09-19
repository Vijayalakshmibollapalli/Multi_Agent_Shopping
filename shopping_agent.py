import os,re,asyncio,json
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph,START,END

load_dotenv()

MCP_URL=os.getenv("MCP_SERVER_URL")
MCP_TOKEN=os.getenv("FASTMCP_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL","openai/gpt-oss-20b")

if not MCP_TOKEN: raise RuntimeError("FASTMCP_TOKEN is missing in .env")
if not GROQ_API_KEY: raise RuntimeError("GROQ_API_KEY is missing in .env")

llm=ChatGroq(api_key=GROQ_API_KEY,model=GROQ_MODEL,temperature=0,max_tokens=1100)

client=MultiServerMCPClient({"shopping":{"url":MCP_URL,"transport":"streamable_http","headers":{"Authorization":f"Bearer {MCP_TOKEN}"}}})
tools_cache=None

async def get_tools():
    global tools_cache
    if tools_cache is None: tools_cache={t.name:t for t in await client.get_tools()}
    return tools_cache

def txt(x):
    if isinstance(x,str): return x
    if isinstance(x,list): return "\n".join(i.get("text",str(i)) if isinstance(i,dict) else str(i) for i in x)
    if isinstance(x,dict): return x.get("text",str(x))
    return str(x)

def trim(x,n):
    return txt(x)[:n]

def get_json(x):
    m=re.search(r"\{.*\}",x,re.S)
    try: return json.loads(m.group()) if m else {}
    except: return {}

class State(TypedDict,total=False):
    query:str
    requirements:str
    products:str
    prices:str
    reviews:str
    comparisons:str
    recommendation:str

async def requirements(s):
    prompt=f"""Analyze this shopping request.

REQUEST:
{s["query"]}

Return only JSON:
{{"product_type":"","budget":"","purpose":"","must_have":[],"preferred":[],"avoid":[],"important":[]}}

Do not invent information."""
    r=await llm.ainvoke(prompt)
    return {"requirements":json.dumps(get_json(r.content),ensure_ascii=False)}

async def research_one(tool,query,limit):
    t=await get_tools()
    if tool not in t: return ""
    return trim(await t[tool].ainvoke({"query":query}),limit)

async def research(s):
    q=f"Request: {s['query']}\nRequirements: {s['requirements']}"
    p,pr,r,c=await asyncio.gather(
        research_one("search_products",q+"\nFind real matching products and relevant specifications.",2800),
        research_one("search_prices",q+"\nFind current prices and availability.",2200),
        research_one("search_reviews",q+"\nFind actual reviews, pros, cons and problems.",2200),
        research_one("search_comparison",q+"\nFind useful alternatives and comparisons.",1600)
    )
    return {"products":p,"prices":pr,"reviews":r,"comparisons":c}

async def recommend(s):
    prompt=f"""You are an evidence-based shopping recommendation agent.

REQUEST:
{s["query"]}

REQUIREMENTS:
{s["requirements"]}

PRODUCT DATA:
{s["products"]}

PRICE DATA:
{s["prices"]}

REVIEW DATA:
{s["reviews"]}

COMPARISON DATA:
{s["comparisons"]}

RULES:
- Recommend only products supported by evidence.
- Never invent names, prices, specifications or reviews.
- Never mix specifications between models.
- Respect the user's budget and requirements.
- Show only details relevant to the request.
- Missing information = Not verified.
- Conflicting sources = Conflicting evidence.
- Do not claim a feature provides a benefit unless the evidence supports it.
- Do not use words such as best, strongest, excellent or exceptional unless clearly supported by comparison evidence.
- Reviews are Verified only when actual review evidence is present.
- Keep the response short enough to finish completely.
- Do not use #, ## or **.
- Use plain text headings.
- Maximum 2 Pros.
- Maximum 2 Cons.
- Maximum 3 Alternatives.
- Do not include Sources section.

OUTPUT:

Recommended Choice
Product: exact model
Current Price: price or Not verified

Why It Matches
- reason
- reason

Key Details
- relevant feature: value
- relevant feature: value
- relevant feature: value
- relevant feature: value

Pros
- advantage
- advantage

Cons
- limitation
- limitation

Verification
- Price: status
- Specifications: status
- Reviews: status

Alternatives
1. model - price
2. model - price
3. model - price

Final Recommendation
One short evidence-based sentence."""
    r=await llm.ainvoke(prompt)
    return {"recommendation":r.content.strip()}

graph=StateGraph(State)
graph.add_node("requirements",requirements)
graph.add_node("research",research)
graph.add_node("recommend",recommend)
graph.add_edge(START,"requirements")
graph.add_edge("requirements","research")
graph.add_edge("research","recommend")
graph.add_edge("recommend",END)

shopping_graph=graph.compile()

async def run_shopping_agent(query):
    if not query.strip(): return "Please enter a shopping request."
    r=await shopping_graph.ainvoke({"query":query.strip()})
    return r.get("recommendation","No recommendation generated.")

if __name__=="__main__":
    print(asyncio.run(run_shopping_agent("Best laptop under ₹70000 for programming")))