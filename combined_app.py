"""
COMBINED APP: Bank API + Dashboard for Render deployment
"""
from fastapi import FastAPI, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import sys
from fastapi import Cookie as FastAPICookie

template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
templates = Jinja2Templates(directory=template_dir)

@app.get("/dashboard")
    
    
    
    
    
    # Try to verify token
    try:
        from bank_auth import verify_magic_link
        email = verify_magic_link(session, mark_used=False)
        if not email:
            email = verify_magic_link(session, mark_used=False)  # Retry
    except ImportError:
        print(f"⚠️ Using mock verification")
        email = "test@example.com"
    
    if not email:
        print("🎯 Redirecting to /login (invalid token)")
        return RedirectResponse("/login")
    
    print(f"🎯 SUCCESS! Showing dashboard for {email}")
    
    # Get balance
    balance = 100  # Mock - replace with your logic
    
    # Use same template directory as frontpage
    template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
    templates = Jinja2Templates(directory=template_dir)
    
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



try:
    from dashboard.app import app as dashboard_app
    
    
except ImportError as e:
    print(f"⚠ Could not import dashboard: {e}")

# 2. Import and include token/auth routes
try:
    from auth_routes import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    print("✓ Auth routes included")
except ImportError as e:
    print(f"⚠ Could not import auth routes: {e}")

# ========== MOUNT BANK API ==========
print("🔧 Loading Bank API...")
try:
    # Import bank app
    from central_bank import app as bank_app
    # Mount at /api
    
    
except Exception as e:
    print(f"❌ Failed to load Bank API: {e}")

    
from fastapi.templating import Jinja2Templates
import os

# Update your public_root function:
@app.get("/")
async def public_root(request: Request):
    """Public frontpage - NO login required"""
    # Try dashboard/templates FIRST since that's where they are
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "dashboard", "templates"),  # ← THIS ONE
        os.path.join(os.path.dirname(__file__), "templates"),
        "templates",
        "./templates"
    ]
    
    for template_dir in possible_paths:
        frontpage_path = os.path.join(template_dir, "frontpage.html")
        print(f"Checking: {frontpage_path} -> {os.path.exists(frontpage_path)}")
        if os.path.exists(frontpage_path):
            print(f"✅ Found frontpage at: {frontpage_path}")
            templates = Jinja2Templates(directory=template_dir)
            return templates.TemplateResponse(
                "frontpage.html", 
                {"request": request, "app_name": "Prompts Alchemy"}
            )

@app.get("/login")
async def login_page(request: Request):
    """Login form"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_request(request: Request, email: str = Form(...)):
    try:
        print(f"📧 Login attempt for: {email}")
        
        # Generate a token
        import secrets
        token = secrets.token_urlsafe(32)
        print(f"🔑 Generated token: {token[:20]}...")
        
        # Save token to auth system
        try:
            import auth
            auth.store_magic_token(email, token)  # or whatever function exists
        except ImportError:
            print(f"⚠️ Could not save token")
        
        # Send email with token
        try:
            import email_service
            email_service.send_magic_link_email(email, token)  # ← ADD TOKEN
            print(f"✅ Magic link sent to {email}")
        except ImportError:
            print(f"⚠️ email_service not found")
            # Show token in console for testing
            print(f"🔗 TEST LINK: https://promptsalchemy.com/auth?token={token}")
        
        # Redirect to check-email
        return RedirectResponse(f"/check-email?email={email}", status_code=303)
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(f"/login?error={str(e)[:50]}")

@app.get("/auth")
async def auth_callback(token: str):
    print(f"🔐 AUTH: Setting cookie for token {token[:20]}...")
    
    response = RedirectResponse("/dashboard")
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        max_age=3600,
        samesite="lax"
    )
    
    print(f"🔐 AUTH: Cookie set, redirecting to /dashboard")
    print(f"🔐 AUTH: Response headers: {dict(response.headers)}")
    
    return response


# ========== SIMPLE DASHBOARD MOUNT ==========


try:
    # Import the module directly
    
    
    
    # Get the FastAPI app instance
    
    
    
except Exception as e:
    print(f"❌ Mount failed: {e}")

@app.get("/debug-templates")
async def debug_templates():
    import glob
    templates = glob.glob("**/*.html", recursive=True)
    return {
        "current_dir": os.getcwd(),
        "this_file": __file__,
        "found_templates": templates,
        "frontpage_exists": os.path.exists("templates/frontpage.html")
    }


# ========== HEALTH ENDPOINTS ==========
@app.get("/health")
async def health_check():
    """Health check for Render/load balancers"""
    return {
        "status": "healthy",
        "service": "prompts-alchemy-combined",
        "version": "2.0.0"
    }


@app.get("/frontpage")
async def frontpage_route(request: Request):
    """Explicit frontpage route with debugging"""
    import os
    
    print("=" * 60)
    print("🚀 FRONTPAGE ROUTE HIT!")
    
    # Calculate template path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "dashboard", "templates")
    
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Template directory: {template_dir}")
    print(f"📁 Directory exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        print(f"📁 Files in directory: {os.listdir(template_dir)}")
    
    # Check if frontpage.html exists
    frontpage_path = os.path.join(template_dir, "frontpage.html")
    print(f"📄 Frontpage.html exists: {os.path.exists(frontpage_path)}")
    
    print("=" * 60)
    
    templates = Jinja2Templates(directory=template_dir)
    
    try:
        return templates.TemplateResponse("frontpage.html", {"request": request})
    except Exception as e:
        print(f"❌ Template error: {e}")
        # Fallback to simple response
        from fastapi.responses import HTMLResponse
        return HTMLResponse(f"""
        <h1>Template Error</h1>
        <p>Error: {e}</p>
        <p>Looking for: {frontpage_path}</p>
        <p>Template dir: {template_dir}</p>
        """)

@app.get("/check-email")
async def check_email_page(request: Request, email: str):
    template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
    templates = Jinja2Templates(directory=template_dir)
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email
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

@app.get("/debug-routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": list(route.methods) if hasattr(route, "methods") else []
        })
    return {"routes": routes}
    
print(f"🚨 LOADED: {__file__}")

# In combined_app.py - DEBUG VERSION
print(f"🔧 COMBINED_APP LOADING: {__file__}")

try:
    
    
except Exception as e:
    print(f"❌ Mount failed: {e}")
    import traceback
    traceback.print_exc()
    # NO fallback route - let /dashboard 404


dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
print(f"🔧 Path: {dashboard_path}")
print(f"🔧 Exists: {os.path.exists(dashboard_path)}")
        
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
