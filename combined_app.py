"""
COMBINED APP: Bank API + Dashboard for Render deployment
"""
from fastapi import FastAPI, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dashboard.app import app as dashboard_app
import os
import sys
from fastapi import Cookie as FastAPICookie

print("=== DEBUG IMPORTS ===")
print("Cookie imported?", "Cookie" in dir())

# Define dashboard_path before using it
dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")


# Create main app
app = FastAPI(
    title="Prompts Alchemy",
    description="AI Wizards with Token Economy",
    version="2.0.0"
)

# CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(dashboard_path, "static")), name="static")

# Pass template directory to dashboard app
#dashboard_app.state.template_dir = os.path.join(dashboard_path, "templates")


try:
    from dashboard.app import app as dashboard_app
    # Mount the entire dashboard app under /dashboard
    app.mount("/dashboard", dashboard_app)
    print("✓ Dashboard mounted at /dashboard")
except ImportError as e:
    print(f"⚠ Could not import dashboard: {e}")

# 2. Import and include token/auth routes
try:
    from auth_routes import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    print("✓ Auth routes included")
except ImportError as e:
    print(f"⚠ Could not import auth routes: {e}")

# 3. Define root routes in combined_app.py itself
@app.get("/")
async def root():
    return RedirectResponse("/login")


# ========== MOUNT BANK API ==========
print("🔧 Loading Bank API...")
try:
    # Import bank app
    from central_bank import app as bank_app
    # Mount at /api
    app.mount("/api", bank_app)
    print("✅ Bank API mounted at /api")
except Exception as e:
    print(f"❌ Failed to load Bank API: {e}")

# ========== MOUNT DASHBOARD ==========
print("🔧 Loading Dashboard...")
try:
    # Add dashboard to Python path
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")
    sys.path.insert(0, dashboard_path)
    
    # Import dashboard app
    from app import app as dashboard_app
    # Mount at root /
    app.mount("/", dashboard_app)
    print("✅ Dashboard mounted at /")
except Exception as e:
    print(f"❌ Failed to load Dashboard: {e}")
    import traceback
    traceback.print_exc()


# ========== HEALTH ENDPOINTS ==========
@app.get("/health")
async def health_check():
    """Health check for Render/load balancers"""
    return {
        "status": "healthy",
        "service": "prompts-alchemy-combined",
        "version": "2.0.0"
    }

# In combined_app.py
@app.get("/")
async def root(request: Request, session: str = Cookie(default=None)):
    """Server decides: frontpage or dashboard"""
    # Check if user has valid session
    if session and verify_magic_link(session, mark_used=False):
        # User is logged in - redirect to dashboard
        return RedirectResponse("/dashboard")
    else:
        # User not logged in - show public frontpage
        template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
        templates = Jinja2Templates(directory=template_dir)
        return templates.TemplateResponse("frontpage.html", {"request": request})

@app.get("/dashboard")  
async def dashboard_home(request: Request, session: str = Cookie(default=None)):
    """Main dashboard - requires login"""
    print(f"🎯 ROOT ROUTE: Session cookie present? {'YES' if session else 'NO'}")
    
    if not session:
        print("🎯 Redirecting to /login (no session)")
        return RedirectResponse("/login")
    
    print(f"🔓 ROOT: Session = {session[:30] if session else 'None'}")
    email = verify_magic_link(session, mark_used=False)
    print(f"🔓 ROOT: Verified as {email}")
    
    if not email:
        print("🎯 Redirecting to /login (invalid session)")
        return RedirectResponse("/login")
    
    print(f"🎯 SUCCESS! Showing dashboard for {email}")
    
    balance = get_user_balance(email)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": email,
        "balance": balance,
        "apps": [
            {"name": "Thumbnail Wizard", "cost": 4, "icon": "🖼️", "status": "ready"},
            {"name": "Document Wizard", "cost": 4, "icon": "📄", "status": "ready"},
            {"name": "Hook Wizard", "cost": 4, "icon": "🎣", "status": "ready"},
            {"name": "Prompt Wizard", "cost": 5, "icon": "✨", "status": "ready"},
            {"name": "Script Wizard", "cost": 3, "icon": "📝", "status": "ready"},
            {"name": "A11y Wizard", "cost": 0, "icon": "♿", "status": "ready"},
        ]
    })

@app.get("/auth")
async def auth_callback(token: str):
    print(f"🔐 AUTH: Token received {token[:30]}...")
    email = verify_magic_link(token, mark_used=False)
    
    if not email:
        print(f"🔓 AUTH: Token = {token[:30]}...")
        email = verify_magic_link(token, mark_used=False)
        print(f"🔓 AUTH: Verified as {email}")
        print(f"🔐 AUTH: Verification SUCCESS for {email}, redirecting to /dashboard")
    
    response = RedirectResponse("/dashboard")
    # Update cookie settings here:
    response.set_cookie(
        key="session", 
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False
    )
    return response

@app.get("/settings")
async def settings_page(request: Request, session: str = Cookie(default=None)):
    if not session:
        return RedirectResponse("/login")
    
    email = verify_magic_link(session, mark_used=False)
    if not email:
        return RedirectResponse("/login")
    
    balance = get_user_balance(email)
    
    # DEFINE current_plan here (mock for now)
    current_plan = "Free Tier"  # TODO: Get from database
    tokens_per_month = 15
    renewal_date = "2024-02-24"
    
    print(f"🔧 SETTINGS DEBUG: current_plan = {current_plan}")
    print(f"🔧 SETTINGS DEBUG: user_email = {email}")
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user_email": email,
        "balance": balance,
        "current_plan": current_plan,
        "tokens_per_month": tokens_per_month,
        "renewal_date": renewal_date
    })

@app.post("/generate-prompt")
async def generate_prompt(
    request: Request,
    goal: str = Form(...),
    audience: str = Form(...),
    platform: str = Form(...),
    style: str = Form(...),
    tone: str = Form(...),
    session: str = Cookie(default=None)
):
    """Generate a prompt using DeepSeek API with token checking"""
    
    # 1. AUTHENTICATION
    if not session:
        return RedirectResponse("/login?next=/prompt-wizard")
    
    email = verify_magic_link(session, mark_used=False)
    if not email:
        return RedirectResponse("/login")
    
    # 2. TOKEN CHECK (5 tokens for Prompt Wizard)
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Check balance
            balance_response = await client.get(
                f"http://localhost:8001/balance?email={email}",
                timeout=5.0
            )
            
            if balance_response.status_code == 200:
                balance = balance_response.json().get("balance", 0)
                if balance < 5:
                    return templates.TemplateResponse("insufficient_tokens.html", {
                        "request": request,
                        "balance": balance,
                        "required": 5,
                        "app_name": "Prompt Wizard"
                    })
            else:
                return layout("Bank Error", 
                    "<div class='card'><h2>Token system unavailable</h2></div>")
    except Exception as e:
        print(f"Token check error: {e}")
        return layout("System Error", 
            "<div class='card'><h2>Cannot connect to token system</h2></div>")
    
    # 3. DEEPSEEK API CALL
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return layout("Error", 
            "<div class='card'><h2>API not configured</h2><p>DeepSeek API key missing.</p></div>")
    
    prompt_text = f"""
    Create a {style} prompt for {audience} to achieve this goal: {goal}.
    Platform: {platform}
    Desired tone: {tone}
    
    Provide a complete, ready‑to‑use prompt.
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a prompt engineering expert."},
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated = result["choices"][0]["message"]["content"]
            
            # 4. DEDUCT TOKENS AFTER SUCCESS
            try:
                async with httpx.AsyncClient() as client:
                    spend_data = {
                        "email": email,
                        "app_id": "prompt_wizard",
                        "tokens": 5,
                        "description": f"Prompt: {goal[:50]}..."
                    }
                    spend_response = await client.post(
                        "http://localhost:8001/spend",
                        json=spend_data,
                        timeout=5.0
                    )
                    if spend_response.status_code != 200:
                        print(f"Token spend failed but prompt generated: {spend_response.text}")
            except Exception as e:
                print(f"Token spend error: {e}")
            
            # 5. RETURN RESULT
            return templates.TemplateResponse("prompt_result.html", {
                "request": request,
                "goal": goal,
                "audience": audience,
                "platform": platform,
                "style": style,
                "tone": tone,
                "generated_prompt": generated,
                "tokens_spent": 5
            })
            
        else:
            return layout("API Error", 
                f"<div class='card'><h2>API Error {response.status_code}</h2>"
                f"<p>{response.text}</p></div>")
                
    except Exception as e:
        return layout("Error", 
            f"<div class='card'><h2>Generation failed</h2><p>{str(e)}</p></div>")

@app.get("/prompt-wizard/intro")
async def prompt_wizard_intro(request: Request, session: str = Cookie(default=None)):
    """Prompt Wizard introduction page"""
    if not session:
        return RedirectResponse("/login?next=/prompt-wizard/intro")
    
    email = verify_magic_link(session, mark_used=False)
    if not email:
        return RedirectResponse("/login")
    
    return templates.TemplateResponse("prompt_wizard_intro.html", {
        "request": request,
        "user_email": email
    })


# In combined_app.py - temporary
@app.get("/debug-all-routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", str(route)),
            "name": getattr(route, "name", "unknown"),
        }
        if hasattr(route, "methods"):
            route_info["methods"] = list(route.methods)
        routes.append(route_info)
    return {"routes": routes}

@app.get("/logout")
async def logout_route():
    """Server-side logout - clears cookies"""
    response = RedirectResponse("/")
    response.delete_cookie("session")
    response.delete_cookie("session_token")  # Add any other auth cookies
    return response

import os

@app.get("/debug-files")
async def debug_files():
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")
    
    return {
        "current_dir": os.path.dirname(__file__),
        "dashboard_exists": os.path.exists(dashboard_path),
        "files_in_dashboard": os.listdir(dashboard_path) if os.path.exists(dashboard_path) else "NOT FOUND",
        "has_init": os.path.exists(os.path.join(dashboard_path, "__init__.py")) if os.path.exists(dashboard_path) else False,
        "has_app": os.path.exists(os.path.join(dashboard_path, "app.py")) if os.path.exists(dashboard_path) else False,
    }

@app.get("/which-app-dashboard")
async def which_app():
    return {"message": "This is COMBINED_APP", "path": "/dashboard"}


# ========== MAIN FOR LOCAL TESTING ==========
"""if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting combined app on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )"""
