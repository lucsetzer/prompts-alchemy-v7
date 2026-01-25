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

@app.get("/", response_class=HTMLResponse)
async def frontpage(request: Request):
    """Serve the frontpage.html template"""
    import os
    from fastapi.templating import Jinja2Templates
    
    # Path to templates in dashboard folder
    template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
    templates = Jinja2Templates(directory=template_dir)
    
    return templates.TemplateResponse("frontpage.html", {
        "request": request
        # No variables needed - pricing hardcoded in HTML
    })

# Mount dashboard at /app (NOT /)
app.mount("/app", dashboard_app)

# ========== MAIN FOR LOCAL TESTING ==========
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting combined app on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
