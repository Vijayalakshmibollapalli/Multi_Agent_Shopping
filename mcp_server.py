import os
import re
import json
import asyncio
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END

load_dotenv()

MCP_URL = os.getenv("MCP_SERVER_URL")
MCP_TOKEN = os.getenv("FASTMCP_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not MCP_URL:
    raise RuntimeError("MCP_SERVER_URL is missing in .env")

if not MCP_TOKEN:
    raise RuntimeError("FASTMCP_TOKEN is missing in .env")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing in .env")

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0, max_tokens=1600)

client = MultiServerMCPClient({"shopping": {"url": MCP_URL, "transport": "streamable_http", "headers": {"Authorization": f"Bearer {MCP_TOKEN}"}}})

tools_cache = None
tools_lock = asyncio.Lock()

async def get_tools():
    global tools_cache
    if tools_cache is None:
        async with tools_lock:
            if tools_cache is None:
                tools = await client.get_tools()
                tools_cache = {tool.name: tool for tool in tools}
                print("MCP tools:", list(tools_cache.keys()))
    return tools_cache

def txt(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(txt(item) for item in value)
    if isinstance(value, dict):
        for key in ["text", "content", "output", "response"]:
            if key in value:
                return txt(value[key])
        return json.dumps(value, ensure_ascii=False)
    if hasattr(value, "content"):
        return txt(value.content)
    return str(value)

def trim(value, limit):
    return txt(value).strip()[:limit]

def get_json(value):
    text = txt(value).replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except Exception:
        return {}

def extract_urls(text):
    urls = re.findall(r"https?://[^\s<>\]\)\"']+", txt(text))
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;:)]}")
        if url not in cleaned:
            cleaned.append(url)
    return cleaned[:8]

def clean_model_name(name):
    name = txt(name).strip()
    name = re.sub(r"^[\-\*\d\.\)\s]+", "", name)
    name = re.sub(r"^(product|model|name)\s*[:\-]\s*", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" .,:;-")

def normalize_name(name):
    return re.sub(r"[^a-z0-9]+", " ", clean_model_name(name).lower()).strip()

GENERIC_NAMES = {
    "laptop",
    "laptops",
    "phone",
    "phones",
    "smartphone",
    "smartphones",
    "tablet",
    "tablets",
    "television",
    "televisions",
    "tv",
    "tvs",
    "monitor",
    "monitors",
    "keyboard",
    "keyboards",
    "mouse",
    "mice",
    "headphones",
    "earbuds",
    "earphones",
    "shoes",
    "shoe",
    "chair",
    "chairs",
    "office chair",
    "refrigerator",
    "refrigerators",
    "washing machine",
    "washing machines",
    "air conditioner",
    "air conditioners",
    "camera",
    "cameras",
    "watch",
    "watches",
    "smartwatch",
    "smartwatches",
    "speaker",
    "speakers",
    "printer",
    "printers",
    "gpu",
    "graphics card",
    "graphics cards",
    "product",
    "products",
    "item",
    "items"
}

RETAILERS = {
    "amazon",
    "flipkart",
    "croma",
    "myntra",
    "walmart",
    "reliance digital",
    "reliance",
    "tata cliq",
    "tatacliq",
    "vijay sales",
    "best buy",
    "asus",
    "dell",
    "hp",
    "lenovo",
    "acer",
    "samsung",
    "apple"
}

def valid_candidate(name):
    name = clean_model_name(name)
    if not name:
        return False
    if len(name) < 4:
        return False
    if len(name) > 100:
        return False
    if len(name.split()) > 12:
        return False
    normalized = normalize_name(name)
    if normalized in GENERIC_NAMES:
        return False
    bad_prefixes = (
        "best ",
        "top ",
        "buy ",
        "latest ",
        "cheap ",
        "budget ",
        "best deal ",
        "review of ",
        "reviews of ",
        "top 10 ",
        "top 5 "
    )
    if name.lower().startswith(bad_prefixes):
        return False
    return True

def is_retailer(name):
    normalized = normalize_name(name)
    return normalized in RETAILERS

def is_generic_category_name(name, product_type):
    normalized = normalize_name(name)
    product_type = normalize_name(product_type)
    if normalized in GENERIC_NAMES:
        return True
    if product_type and normalized == product_type:
        return True
    return False

def candidate_supported_by_evidence(candidate, evidence):
    candidate_normalized = normalize_name(candidate)
    evidence_normalized = normalize_name(evidence)
    if not candidate_normalized:
        return False
    if candidate.lower() in evidence.lower():
        return True
    candidate_words = candidate_normalized.split()
    evidence_words = evidence_normalized.split()
    if len(candidate_words) >= 2:
        matched = sum(1 for word in candidate_words if word in evidence_words)
        required = max(2, len(candidate_words) - 1)
        return matched >= required
    return candidate_normalized in evidence_normalized

def extract_candidate_lines(text, product_type):
    candidates = []
    lines = txt(text).splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = re.sub(r"^\[SOURCE\s+\d+\]", "", line, flags=re.I).strip()

        if line.lower().startswith("title:"):
            line = line[6:].strip()

        elif line.lower().startswith("content:"):
            line = line[8:].strip()

        elif line.lower().startswith("url:"):
            continue

        price_patterns = [
            r"(.{3,100})\s+(?:₹|Rs\.?|INR|\$)\s?[\d,]+",
            r"(?:model|product)\s*[:\-]\s*(.{3,100})",
            r"(?:called|named)\s+(.{3,100})"
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, line, re.I)

            for match in matches:
                candidate = clean_model_name(match)

                candidate = re.sub(
                    r"\s+(?:price|cost|specifications|features|review|rating|ratings|available).*$",
                    "",
                    candidate,
                    flags=re.I
                )

                if not valid_candidate(candidate):
                    continue

                if is_retailer(candidate):
                    continue

                if is_generic_category_name(candidate, product_type):
                    continue

                candidates.append(candidate)

    unique = []
    seen = set()

    for candidate in candidates:
        key = normalize_name(candidate)

        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    return unique

async def extract_candidates(product_data, price_data, comparison_data, query, requirements):
    product_data = trim(product_data, 5000)
    price_data = trim(price_data, 4000)
    comparison_data = trim(comparison_data, 3000)

    combined = f"""USER REQUEST:
{query}

REQUIREMENTS:
{requirements}

PRODUCT RESEARCH:
{product_data}

PRICE RESEARCH:
{price_data}

COMPARISON RESEARCH:
{comparison_data}"""

    prompt = f"""You are a product candidate extraction agent for a universal shopping assistant.

USER REQUEST:
{query}

REQUIREMENTS:
{requirements}

RESEARCH:
{combined}

Extract real purchasable products that are explicitly mentioned in the research.

IMPORTANT:
- This assistant supports ANY shopping category.
- Products can be electronics, appliances, clothes, shoes, furniture, cameras, books, accessories, beauty products, sports products, etc.
- Do NOT assume the category is laptop or electronics.
- Extract actual product names, not categories.
- Brand + product name is acceptable.
- Brand + model is preferred when available.
- A model number is NOT mandatory.
- Never invent a product.
- Never return a retailer.
- Never return an article title.
- Never return a generic category.
- Extract only products supported by the research.
- Maximum 8 products.
- Return JSON only.

Examples of valid products:
- Dell Inspiron 15 5530
- ASUS Vivobook S15 OLED
- Nike Revolution 7
- Samsung Galaxy A55
- Sony WH-1000XM5
- IKEA Markus
- LG 260 L Refrigerator

Examples of invalid products:
- laptop
- shoes
- phone
- best laptops under 70000
- Amazon
- Flipkart

Return:

{{"candidates":["product 1","product 2","product 3"]}}"""

    candidates = []

    try:
        result = await llm.ainvoke(prompt)
        data = get_json(result.content)
        candidates = data.get("candidates", [])

        if not isinstance(candidates, list):
            candidates = []

    except Exception as e:
        print("Candidate extraction warning:", repr(e))

    evidence = product_data + "\n" + price_data + "\n" + comparison_data

    try:
        requirement_data = get_json(requirements)
    except Exception:
        requirement_data = {}

    product_type = requirement_data.get("product_type", "")

    verified = []
    seen = set()

    for candidate in candidates:
        candidate = clean_model_name(candidate)
        normalized = normalize_name(candidate)

        if not valid_candidate(candidate):
            continue

        if is_retailer(candidate):
            continue

        if is_generic_category_name(candidate, product_type):
            continue

        if normalized in seen:
            continue

        if candidate_supported_by_evidence(candidate, evidence):
            verified.append(candidate)
            seen.add(normalized)

    fallback_candidates = extract_candidate_lines(product_data + "\n" + price_data + "\n" + comparison_data, product_type)

    for candidate in fallback_candidates:
        normalized = normalize_name(candidate)

        if normalized in seen:
            continue

        if candidate_supported_by_evidence(candidate, evidence):
            verified.append(candidate)
            seen.add(normalized)

    return verified[:8]

class State(TypedDict, total=False):
    query: str
    requirements: str
    products: str
    prices: str
    reviews: str
    comparisons: str
    candidates: str
    recommendation: str

async def requirements_node(state: State):
    print("Understanding shopping requirements...")

    prompt = f"""Analyze this shopping request.

USER REQUEST:
{state["query"]}

Extract only information explicitly stated by the user.

Return JSON only.

Format:
{{
"product_type":"",
"budget":"",
"purpose":"",
"must_have":[],
"preferred":[],
"avoid":[],
"important":[]
}}

Rules:
- Do not invent requirements.
- Do not assume laptop or electronics.
- Support any shopping category.
- Missing values must be empty."""

    try:
        result = await llm.ainvoke(prompt)
        requirements = get_json(result.content)

    except Exception as e:
        print("Requirement extraction warning:", repr(e))
        requirements = {
            "product_type": "",
            "budget": "",
            "purpose": "",
            "must_have": [],
            "preferred": [],
            "avoid": [],
            "important": []
        }

    return {
        "requirements": json.dumps(
            requirements,
            ensure_ascii=False
        )
    }

async def research_one(tool_name, query, limit):
    tools = await get_tools()
    tool = tools.get(tool_name)

    if tool is None:
        print("Missing MCP tool:", tool_name)
        return ""

    try:
        result = await tool.ainvoke({"query": query})
        return trim(result, limit)

    except Exception as e:
        print(f"{tool_name} error:", repr(e))
        return ""

async def research_node(state: State):
    print("Starting parallel product research...")

    research_query = f"""USER REQUEST:
{state["query"]}

REQUIREMENTS:
{state["requirements"]}

Important:
Research the exact shopping request.
Support any product category.
Do not assume laptops or electronics."""

    products_task = research_one(
        "search_products",
        research_query + "\nFind multiple real purchasable products, brands, product names, models, variants and relevant specifications.",
        5000
    )

    prices_task = research_one(
        "search_prices",
        research_query + "\nFind current prices, availability and relevant retailer or official-store pricing for matching products.",
        4000
    )

    reviews_task = research_one(
        "search_reviews",
        research_query + "\nFind expert reviews, user reviews, ratings, pros, cons, quality, reliability and common problems.",
        3500
    )

    comparisons_task = research_one(
        "search_comparison",
        research_query + "\nFind competing products, alternatives, comparable products and differences.",
        3000
    )

    products, prices, reviews, comparisons = await asyncio.gather(
        products_task,
        prices_task,
        reviews_task,
        comparisons_task
    )

    print("Product research completed.")

    return {
        "products": products,
        "prices": prices,
        "reviews": reviews,
        "comparisons": comparisons
    }

async def candidate_node(state: State):
    print("Validating product candidates...")

    candidates = await extract_candidates(
        state.get("products", ""),
        state.get("prices", ""),
        state.get("comparisons", ""),
        state["query"],
        state.get("requirements", "{}")
    )

    print("Verified candidates:", candidates)

    return {
        "candidates": json.dumps(
            candidates,
            ensure_ascii=False
        )
    }

def find_price_for_product(product, text):
    text = txt(text)

    if not text:
        return "Not verified"

    product_words = [
        word.lower()
        for word in re.findall(r"[A-Za-z0-9]+", product)
    ]

    if not product_words:
        return "Not verified"

    best_price = None
    best_score = 0

    for line in text.splitlines():
        lower = line.lower()

        matching_words = sum(
            1 for word in product_words
            if word in lower
        )

        if matching_words < min(2, len(product_words)):
            continue

        match = re.search(
            r"(₹\s?[\d,]+(?:\.\d+)?|\bRs\.?\s?[\d,]+(?:\.\d+)?|\bINR\s?[\d,]+(?:\.\d+)?|\$\s?[\d,]+(?:\.\d+)?)",
            line,
            re.I
        )

        if match and matching_words > best_score:
            best_score = matching_words
            best_price = match.group(1)

    return best_price if best_price else "Not verified"

def price_value(price):
    if not price:
        return None

    match = re.search(
        r"[\d,]+(?:\.\d+)?",
        str(price)
    )

    if not match:
        return None

    try:
        return float(
            match.group().replace(",", "")
        )
    except Exception:
        return None

def extract_budget(query):
    patterns = [
        r"(?:under|below|less than|within|upto|up to)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        r"(?:maximum|max|max budget|budget of)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.I)

        if match:
            try:
                return float(
                    match.group(1).replace(",", "")
                )
            except Exception:
                return None

    return None

def product_price_map(candidates, price_text):
    result = {}

    for candidate in candidates:
        result[candidate] = find_price_for_product(
            candidate,
            price_text
        )

    return result

async def recommend_node(state: State):
    print("Preparing final recommendation...")

    try:
        candidates = json.loads(
            state.get("candidates", "[]")
        )
    except Exception:
        candidates = []

    products = trim(
        state.get("products", ""),
        3500
    )

    prices = trim(
        state.get("prices", ""),
        3000
    )

    reviews = trim(
        state.get("reviews", ""),
        2200
    )

    comparisons = trim(
        state.get("comparisons", ""),
        1600
    )

    urls = []

    for text in [
        products,
        prices,
        reviews,
        comparisons
    ]:
        for url in extract_urls(text):
            if url not in urls:
                urls.append(url)

    if not candidates:
        fallback = """Recommended Choice
Product: Recommendation unavailable
Current Price: Not verified

Why It Matches
- Research was completed, but no sufficiently verified product candidate was identified.

Key Details
- Product details could not be reliably matched to an exact product.

Pros
- Research sources were found.

Cons
- Exact product verification was insufficient.

Verification
- Price: Not verified
- Specifications: Not verified
- Reviews: Not verified

Alternatives
No verified alternatives found.

Final Recommendation
The research should be checked again before making a purchase."""

        if urls:
            fallback += "\n\nSources\n" + "\n".join(urls[:8])

        return {
            "recommendation": fallback
        }

    budget = extract_budget(
        state["query"]
    )

    prices_for_candidates = product_price_map(
        candidates,
        prices
    )

    research = f"""PRODUCT RESEARCH:
{products}

PRICE RESEARCH:
{prices}

REVIEW RESEARCH:
{reviews}

COMPARISON RESEARCH:
{comparisons}"""

    prompt = f"""You are the final decision-making agent for a universal shopping assistant.

USER REQUEST:
{state["query"]}

REQUIREMENTS:
{state["requirements"]}

VERIFIED PRODUCTS:
{json.dumps(candidates, ensure_ascii=False)}

PRICE EVIDENCE:
{json.dumps(prices_for_candidates, ensure_ascii=False)}

USER BUDGET:
{budget if budget is not None else "Not explicitly detected"}

RESEARCH:
{research}

Select exactly ONE product.

STRICT RULES:
- Select only from VERIFIED PRODUCTS.
- Never invent a product.
- Never invent a price.
- Never invent specifications.
- Never invent ratings.
- Never invent reviews.
- Never invent URLs.
- Respect the user's requirements.
- Respect the user's budget when one is provided.
- If price is not verified, write Not verified.
- If specifications are missing, write Not verified.
- If reviews are missing, write Not verified.
- Never mix information between products.
- Alternatives must come from VERIFIED PRODUCTS.
- Maximum 3 alternatives.
- Maximum 2 pros.
- Maximum 2 cons.
- Do not return generic categories.
- Do not assume the product is a laptop.
- Do not assume the product is electronics.
- Support any shopping category.
- No Markdown.
- No # symbols.
- No ** symbols.
- Do not include URLs.
- Return plain text only.

OUTPUT:

Recommended Choice
Product: exact verified product
Current Price: verified price or Not verified

Why It Matches
- reason
- reason

Key Details
- specification: value
- specification: value
- specification: value

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
1. exact verified product - price or Not verified
2. exact verified product - price or Not verified
3. exact verified product - price or Not verified

Final Recommendation
One short sentence."""

    recommendation = None

    for attempt in range(2):
        try:
            result = await llm.ainvoke(prompt)

            recommendation = txt(
                result.content
            ).strip()

            if recommendation:
                break

        except Exception as e:
            print(
                "Recommendation error:",
                repr(e)
            )

            if attempt == 0:
                print("Waiting before retry...")
                await asyncio.sleep(5)

    if not recommendation:
        affordable = []

        for candidate in candidates:
            price = find_price_for_product(
                candidate,
                prices
            )

            value = price_value(price)

            if budget is None or value is None or value <= budget:
                affordable.append(
                    (candidate, price, value)
                )

        if not affordable:
            best = candidates[0]
            price = find_price_for_product(
                best,
                prices
            )
        else:
            verified_affordable = [
                item
                for item in affordable
                if item[2] is not None
            ]

            if verified_affordable:
                best, price, _ = verified_affordable[0]
            else:
                best, price, _ = affordable[0]

        alternatives = []

        for candidate in candidates:
            if normalize_name(candidate) == normalize_name(best):
                continue

            alt_price = find_price_for_product(
                candidate,
                prices
            )

            alternatives.append(
                f"{len(alternatives)+1}. {candidate} - {alt_price}"
            )

            if len(alternatives) == 3:
                break

        recommendation = f"""Recommended Choice
Product: {best}
Current Price: {price}

Why It Matches
- {best} is a verified product identified in the research.
- It matches the user's shopping requirements.

Key Details
- Specifications: Not verified
- Availability: Not verified
- Performance: Not verified

Pros
- Verified product found in research.
- Relevant to the user's request.

Cons
- Complete specifications were not fully verified.
- Current availability may change.

Verification
- Price: {price}
- Specifications: Not verified
- Reviews: Not verified

Alternatives
{chr(10).join(alternatives) if alternatives else "No verified alternatives found."}

Final Recommendation
{best} is the strongest verified candidate from the available research."""

    if urls:
        recommendation += (
            "\n\nSources\n" +
            "\n".join(urls[:8])
        )

    return {
        "recommendation": recommendation
    }

graph = StateGraph(State)

graph.add_node(
    "requirements",
    requirements_node
)

graph.add_node(
    "research",
    research_node
)

graph.add_node(
    "candidates",
    candidate_node
)

graph.add_node(
    "recommend",
    recommend_node
)

graph.add_edge(
    START,
    "requirements"
)

graph.add_edge(
    "requirements",
    "research"
)

graph.add_edge(
    "research",
    "candidates"
)

graph.add_edge(
    "candidates",
    "recommend"
)

graph.add_edge(
    "recommend",
    END
)

shopping_graph = graph.compile()

async def run_shopping_agent(query: str):
    query = query.strip()

    if not query:
        return "Please enter a shopping request."

    print("\nStarting AI Shopping Intelligence...")
    print("Shopping request:", query)

    try:
        result = await shopping_graph.ainvoke(
            {"query": query}
        )

        return result.get(
            "recommendation",
            "No recommendation generated."
        )

    except Exception as e:
        print(
            "Agent execution error:",
            repr(e)
        )
        raise

if __name__ == "__main__":
    test_query = "Best laptop under ₹70000 for programming"
    print(
        asyncio.run(
            run_shopping_agent(test_query)
        )
    )
