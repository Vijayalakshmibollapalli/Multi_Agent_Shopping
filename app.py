from fastapi import FastAPI,Form
from fastapi.responses import HTMLResponse
from shopping_agent import run_shopping_agent

app=FastAPI(title="AI Shopping Intelligence API",version="1.0.0")

HTML="""
<!DOCTYPE html>
<html>
<head>
<title>AI Shopping Intelligence</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6fa;font-family:Arial;color:#172033}.container{max-width:1000px;margin:50px auto;padding:20px}.card{background:white;border-radius:18px;padding:32px;box-shadow:0 8px 30px #0001}h1{margin:0 0 10px;font-size:30px}.sub{color:#555;margin-bottom:25px}.search{display:flex;gap:10px}input{flex:1;padding:15px;border:1px solid #d5d9e2;border-radius:10px;font-size:16px}button{padding:15px 25px;border:0;border-radius:10px;background:#2563eb;color:white;font-size:16px;cursor:pointer}.loading,.result{display:none;margin-top:25px;padding:20px;border-radius:12px}.loading{background:#f8fafc}.result{border:1px solid #e1e5ec}.result pre{white-space:pre-wrap;font:15px Arial;line-height:1.7;margin:0}.error{padding:15px;background:#fff1f2;color:#b91c1c;border-radius:10px}@media(max-width:700px){.search{flex-direction:column}button{width:100%}}
</style>
</head>
<body>
<div class="container">
<div class="card">
<h1>AI Shopping Intelligence</h1>
<div class="sub">Multi-Agent product research and purchase decision assistant using LangGraph and MCP</div>
<form id="form">
<div class="search">
<input id="query" name="query" placeholder="Example: Best office chair under ₹20000 for long working hours" required>
<button type="submit">Search</button>
</div>
</form>
<div class="loading" id="loading">Researching products, prices and reviews...</div>
<div class="result" id="result"></div>
</div>
</div>
<script>
const form=document.getElementById("form"),query=document.getElementById("query"),loading=document.getElementById("loading"),result=document.getElementById("result");
form.onsubmit=async e=>{
e.preventDefault();loading.style.display="block";result.style.display="none";
try{
const r=await fetch("/search",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"query="+encodeURIComponent(query.value)});
const d=await r.json();
result.innerHTML=d.error?'<div class="error">Error: '+d.error+'</div>':'<pre>'+escapeHtml(d.result)+'</pre>';
}catch(e){result.innerHTML='<div class="error">Request failed: '+escapeHtml(e.toString())+'</div>'}
loading.style.display="none";result.style.display="block";
};
function escapeHtml(x){return x.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
</script>
</body>
</html>
"""

@app.get("/",response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/search")
async def search(query:str=Form(...)):
    try:
        if not query.strip(): return {"error":"Please enter a shopping request."}
        return {"result":await run_shopping_agent(query)}
    except Exception as e:
        return {"error":str(e)}