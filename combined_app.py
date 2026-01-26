"""
COMBINED APP: Bank API + Dashboard for Render deployment
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

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

@app.get("/", response_class=HTMLResponse)
async def frontpage(request: Request):
    """Serve the frontpage.html template"""
    import os
    from fastapi.templating import Jinja2Templates
    
    # DEBUG: Print paths
    print("=" * 60)
    print("DEBUG FRONTPAGE ROUTE")
    print(f"Current file: {__file__}")
    print(f"Current directory: {os.path.dirname(__file__)}")
    
    template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
    print(f"Template directory: {template_dir}")
    print(f"Directory exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        print(f"Files in template directory: {os.listdir(template_dir)}")
    
    templates = Jinja2Templates(directory=template_dir)
    print("=" * 60)
    
    return templates.TemplateResponse("frontpage.html", {
        "request": request
    })
# Mount dashboard at /app (NOT /)
app.mount("/app", dashboard_app)

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
