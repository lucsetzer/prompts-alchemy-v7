from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from pricing import ACCOUNT_TYPES, PRICING  # Your finalized pricing

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def calculate_what_you_get(tier):
    """Exactly what busy creators want to see"""
    tokens = ACCOUNT_TYPES[tier]["tokens"]
    return {
        "tier": tier,
        "monthly_tokens": tokens,
        "monthly_price": ACCOUNT_TYPES[tier]["price"],
        "thumbnail_analyses": f"{tokens // PRICING['thumbnail_wizard']['analyze']}+",
        "scripts": f"{tokens // PRICING['script_wizard']['generate']}+",
        "prompt_optimizations": f"{tokens // PRICING['prompt_wizard']['optimize']}+",
        "hooks": f"{tokens // PRICING['hook_wizard']['generate']}+",
        "best_for": ACCOUNT_TYPES[tier]["best_for"]
    }

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    """Main dashboard showing value proposition"""
    tiers = {}
    for tier_name in ["free", "student", "creator", "agency"]:
        tiers[tier_name] = calculate_what_you_get(tier_name)
    
    return templates.TemplateResponse("homepage.html", {
        "request": request,
        "tiers": tiers,
        "tagline": "AI results for busy creators, no learning curve"
    })

@app.get("/api/what-i-get/{tier}")
def what_i_get_api(tier: str):
    """API endpoint for your existing homepage to call"""
    if tier not in ACCOUNT_TYPES:
        return {"error": "Tier not found"}
    return calculate_what_you_get(tier)

print(f"🚨 LOADED: {__file__}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port from your bank
