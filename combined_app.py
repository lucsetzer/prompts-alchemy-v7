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

template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
templates = Jinja2Templates(directory=template_dir)


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
        
        # Check what's available
        import sys
        print(f"   Python path: {sys.path}")
        
        # Try to import email_service
        try:
            import email_service
            print(f"   ✅ email_service found at: {email_service.__file__}")
            email_service.send_magic_link_email(email)
            print(f"   ✅ Magic link sent")
        except ImportError as ie:
            print(f"   ❌ email_service import failed: {ie}")
            # Simulate for now
            print(f"   📝 Would send magic link to {email}")
        
        # Try to import auth for token generation
        try:
            import auth
            print(f"   ✅ auth found at: {auth.__file__}")
        except ImportError as ie:
            print(f"   ❌ auth import failed: {ie}")
        
        # Redirect
        print(f"   🔀 Redirecting to /check-email")
        return RedirectResponse(
            url=f"/check-email?email={email}",
            status_code=303  # Important for POST→GET redirect
        )
        
    except Exception as e:
        print(f"❌ LOGIN CRASH: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error page
        return HTMLResponse(f"""
        <h1>Login Error</h1>
        <pre>{traceback.format_exc()}</pre>
        <a href="/login">Try Again</a>
        """)


# ========== SIMPLE DASHBOARD MOUNT ==========
print("🔧 Attempting to mount dashboard...")

try:
    # Import the module directly
    import importlib
    dashboard_module = importlib.import_module("dashboard.app")
    
    # Get the FastAPI app instance
    dashboard_app = dashboard_module.app
    
    # Mount it
    app.mount("/dashboard", dashboard_app)
    print("✅ Dashboard mounted at /dashboard")
    
except Exception as e:
    print(f"❌ Mount failed: {e}")
    
    # Create a simple dashboard route as fallback
    @app.get("/dashboard")
    async def dashboard_fallback(request: Request):
        return {
            "error": "Dashboard not mounted",
            "detail": str(e),
            "note": "Check dashboard/app.py exists and has 'app = FastAPI()'"
        }

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
    print("Attempting to import dashboard.app...")
    from dashboard.app import app as dashboard_app
    print(f"✅ Imported dashboard.app from {dashboard_app.__file__}")
    
    app.mount("/dashboard", dashboard_app)
    print("✅ Mounted at /dashboard")
    
except Exception as mount_error:  # Change 'e' to 'mount_error'
    print(f"❌ Mount failed: {mount_error}")
    
    @app.get("/dashboard")
    async def dashboard_fallback(request: Request):
        return {
            "error": "Dashboard mount failed", 
            "detail": str(mount_error)  # Use the captured variable
        }
        
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
