from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from shopping_agent import run_shopping_agent

app = FastAPI(title="AI Shopping Intelligence API", version="1.0.0")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Shopping Intelligence</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#f4f6fb;color:#172033}
.container{max-width:1150px;margin:auto;padding:30px 20px 60px}
.hero{background:linear-gradient(135deg,#172554,#4338ca);padding:42px;border-radius:24px;color:white;box-shadow:0 15px 40px rgba(37,48,120,.2)}
.hero h1{margin:0;font-size:40px}
.hero p{margin:12px 0 0;color:#dbeafe;font-size:16px;line-height:1.6}
.search{display:flex;gap:12px;margin-top:28px}
.search input{flex:1;border:0;border-radius:12px;padding:17px 18px;font-size:16px;outline:none}
.search button{border:0;border-radius:12px;padding:17px 25px;background:white;color:#3730a3;font-weight:700;font-size:15px;cursor:pointer}
.search button:disabled{opacity:.6;cursor:not-allowed}
.panel{background:white;border-radius:20px;padding:26px;margin-top:20px;box-shadow:0 8px 25px rgba(15,23,42,.06)}
.panel h2{margin:0 0 18px;color:#172554}
.examples{display:flex;flex-wrap:wrap;gap:10px}
.example{padding:12px 17px;background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;border-radius:10px;font-weight:700;cursor:pointer}
.example:hover{background:#e0e7ff}
.loading{display:none;text-align:center;padding:30px}
.spinner{width:35px;height:35px;border:4px solid #ddd;border-top:4px solid #4338ca;border-radius:50%;animation:spin 1s linear infinite;margin:auto}
@keyframes spin{to{transform:rotate(360deg)}}
.result{display:none}
.recommendation{background:linear-gradient(135deg,#eef2ff,#f8fafc);border:1px solid #dbe4ff;border-radius:18px;padding:28px}
.small-title{text-transform:uppercase;font-size:13px;font-weight:800;color:#64748b;letter-spacing:.5px}
.product{font-size:30px;font-weight:800;color:#172554;margin:8px 0 10px}
.price{font-size:24px;font-weight:800;color:#15803d}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}
.card{border:1px solid #e2e8f0;background:white;border-radius:18px;padding:23px}
.card h3{margin:0 0 15px;color:#3730a3;font-size:20px}
.card ul{margin:0;padding-left:22px}
.card li{margin:9px 0;line-height:1.5}
.alternative{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:13px;margin-top:9px}
.source{display:block;color:#3730a3;text-decoration:none;border-bottom:1px dashed #a5b4fc;padding:8px 0;word-break:break-all}
.source:hover{text-decoration:underline}
.verdict{background:#ecfdf5;border-left:5px solid #16a34a;padding:17px;border-radius:10px;line-height:1.6}
.error{color:#991b1b;background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:18px}
.badge{display:inline-block;padding:6px 10px;background:#ecfdf5;color:#166534;border-radius:20px;font-size:12px;font-weight:700;margin-bottom:12px}
.universal{margin-top:15px;color:#dbeafe;font-size:14px}
@media(max-width:700px){.container{padding:15px}.hero{padding:28px}.hero h1{font-size:30px}.search{flex-direction:column}.grid{grid-template-columns:1fr}.product{font-size:24px}}
</style>
</head>
<body>
<div class="container">

<div class="hero">
<h1>AI Shopping Intelligence</h1>
<p>AI-powered product research and purchase decision assistant using LangGraph, Remote MCP, Tavily and Groq.</p>
<div class="universal">Search for any product, brand, category, budget or shopping requirement.</div>
<div class="search">
<input id="query" placeholder="Example: Best laptop under ₹70000 for programming">
<button id="analyze" onclick="searchProduct()">Analyze Product</button>
</div>
</div>

<div class="panel">
<h2>Example Searches</h2>
<div class="examples">
<button class="example" onclick="setQuery('Best laptop under ₹70000 for programming')">Laptop</button>
<button class="example" onclick="setQuery('Best phone under ₹30000 with good camera')">Phone</button>
<button class="example" onclick="setQuery('Best running shoes under ₹5000')">Shoes</button>
<button class="example" onclick="setQuery('Best office chair under ₹15000 for long working hours')">Office Chair</button>
<button class="example" onclick="setQuery('Best refrigerator under ₹40000 for family')">Refrigerator</button>
<button class="example" onclick="setQuery('Best camera under ₹60000 for photography')">Camera</button>
<button class="example" onclick="setQuery('Best smartwatch under ₹10000')">Smartwatch</button>
<button class="example" onclick="setQuery('Best headphones under ₹5000 for music')">Headphones</button>
</div>
</div>

<div class="panel loading" id="loading">
<div class="spinner"></div>
<h3>AI Research Agent is working...</h3>
<p id="loadingText">Understanding your requirements...</p>
</div>

<div class="panel result" id="result"></div>

</div>

<script>
function setQuery(value){document.getElementById("query").value=value;document.getElementById("query").focus();}

function esc(value){return String(value||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");}

function parseReport(text){
const report={why:[],details:[],pros:[],cons:[],alternatives:[],sources:[],verification:[]};
const lines=text.split("\\n");
let section="";
lines.forEach(function(line){
const value=line.trim();
if(!value)return;
if(value==="Recommended Choice"){section="recommended";return;}
if(value==="Why It Matches"){section="why";return;}
if(value==="Key Details"){section="details";return;}
if(value==="Pros"){section="pros";return;}
if(value==="Cons"){section="cons";return;}
if(value==="Verification"){section="verification";return;}
if(value==="Alternatives"){section="alternatives";return;}
if(value==="Final Recommendation"){section="verdict";return;}
if(value==="Sources"){section="sources";return;}
if(value.startsWith("Product:")){report.product=value.substring(8).trim();return;}
if(value.startsWith("Current Price:")){report.price=value.substring(14).trim();return;}
if(section==="why"&&value.startsWith("-"))report.why.push(value.substring(1).trim());
else if(section==="details"&&value.startsWith("-"))report.details.push(value.substring(1).trim());
else if(section==="pros"&&value.startsWith("-"))report.pros.push(value.substring(1).trim());
else if(section==="cons"&&value.startsWith("-"))report.cons.push(value.substring(1).trim());
else if(section==="verification"&&value.startsWith("-"))report.verification.push(value.substring(1).trim());
else if(section==="alternatives"&&/^\\d+\\./.test(value))report.alternatives.push(value.replace(/^\\d+\\.\\s*/,""));
else if(section==="verdict")report.verdict=value;
else if(section==="sources"&&value.startsWith("http"))report.sources.push(value);
});
return report;
}

function list(items){
if(!Array.isArray(items)||items.length===0)return "<li>Not available in research.</li>";
return items.map(function(item){return "<li>"+esc(item)+"</li>";}).join("");
}

function render(text){
const report=parseReport(text);
const product=report.product||"Product not identified";
const price=report.price||"Not verified";
const alternatives=report.alternatives||[];
const sources=report.sources||[];
const verification=report.verification||[];

const alternativeHtml=alternatives.length?alternatives.map(function(item){return "<div class='alternative'>"+esc(item)+"</div>";}).join(""):"<div class='alternative'>No reliable alternative was identified.</div>";

const sourceHtml=sources.length?sources.map(function(url){return "<a class='source' href='"+esc(url)+"' target='_blank' rel='noopener noreferrer'>"+esc(url)+"</a>";}).join(""):"<p>No valid source URL was returned by the research.</p>";

const verificationHtml=verification.length?verification.map(function(item){return "<li>"+esc(item)+"</li>";}).join(""):"<li>Verification information not available.</li>";

return "<div class='recommendation'><div class='badge'>AI-POWERED RECOMMENDATION</div><div class='small-title'>Best Recommendation</div><div class='product'>"+esc(product)+"</div><div class='price'>"+esc(price)+"</div></div><div class='grid'><div class='card'><h3>Why This Product</h3><ul>"+list(report.why)+"</ul></div><div class='card'><h3>Key Details</h3><ul>"+list(report.details)+"</ul></div><div class='card'><h3>Pros</h3><ul>"+list(report.pros)+"</ul></div><div class='card'><h3>Cons</h3><ul>"+list(report.cons)+"</ul></div></div><div class='card' style='margin-top:18px'><h3>Verification</h3><ul>"+verificationHtml+"</ul></div><div class='card' style='margin-top:18px'><h3>Alternatives</h3>"+alternativeHtml+"</div><div class='card' style='margin-top:18px'><h3>Sources</h3>"+sourceHtml+"</div><div class='card' style='margin-top:18px'><h3>Final Verdict</h3><div class='verdict'>"+esc(report.verdict||"Verify the current product price and specifications before purchasing.")+"</div></div>";
}

async function searchProduct(){
const query=document.getElementById("query").value.trim();
if(!query){alert("Please enter a shopping request.");return;}

const button=document.getElementById("analyze");
const loading=document.getElementById("loading");
const loadingText=document.getElementById("loadingText");
const result=document.getElementById("result");

const messages=["Understanding your requirements...","Finding relevant products...","Checking current prices...","Analyzing reviews...","Comparing alternatives...","Preparing your recommendation..."];

let index=0;
loadingText.innerText=messages[0];

const timer=setInterval(function(){index=(index+1)%messages.length;loadingText.innerText=messages[index];},2500);

button.disabled=true;
button.innerText="Researching...";
loading.style.display="block";
result.style.display="none";

try{
const response=await fetch("/search",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"query="+encodeURIComponent(query)});
const data=await response.json();

if(!response.ok)throw new Error(data.detail||data.error||"Request failed");

result.innerHTML=render(data.result);
result.style.display="block";
result.scrollIntoView({behavior:"smooth",block:"start"});
}
catch(error){
result.innerHTML="<div class='error'><b>Research could not be completed.</b><br><br>"+esc(error.message)+"</div>";
result.style.display="block";
}
finally{
clearInterval(timer);
loading.style.display="none";
button.disabled=false;
button.innerText="Analyze Product";
}
}

document.getElementById("query").addEventListener("keydown",function(event){if(event.key==="Enter")searchProduct();});
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/search")
async def search(query: str = Form(...)):
    query = query.strip()

    if not query:
        return {"error": "Please enter a shopping request."}

    try:
        result = await run_shopping_agent(query)
        return {"result": result}
    except Exception as e:
        print("API error:", repr(e))
        return {"error": f"Shopping agent failed: {str(e)}"}
