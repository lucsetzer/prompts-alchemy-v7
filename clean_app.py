# clean_app.py
from fastapi import FastAPI, Request, Cookie, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

try:
    from shared.auth import get_db_path
    print("✅ Imported get_db_path from shared.auth")
except ImportError as e:
    print(f"⚠️ Could not import get_db_path: {e}")
    # Fallback
    def get_db_path():
        return "bank.db"

app = FastAPI()

# Define the DB path once, use everywhere
RENDER_DB_PATH = Path("/opt/render/project/src/bank.db")
LOCAL_DB_PATH = Path("bank.db")

# Use environment variable to detect Render
IS_RENDER = os.getenv("RENDER", False)

DB_PATH = RENDER_DB_PATH if IS_RENDER else LOCAL_DB_PATH

@app.on_event("startup")
async def startup_event():
    """Initialize database when app starts"""
    print(f"🚀 Starting on {'RENDER' if IS_RENDER else 'LOCAL'}")
    print(f"📁 Database path: {DB_PATH}")
    
    # Create DB and tables
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS magic_links
                 (token TEXT PRIMARY KEY, email TEXT, created DATETIME, used BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (email TEXT PRIMARY KEY, tokens INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")

# At the top after imports
try:
    from shared.auth import init_database
    init_database()
except ImportError:
    print("⚠️ Could not initialize database")

app = FastAPI()
template_dir = os.path.join(os.path.dirname(__file__), "dashboard", "templates")
templates = Jinja2Templates(directory=template_dir)

# 1. Frontpage
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("frontpage.html", {"request": request})

# 2. Login
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_request(email: str = Form(...)):
    print(f"📧 Login request for: {email}")
    
    # Try to send email
    try:
        from shared.email_service import send_magic_link_email
        magic_link = send_magic_link_email(email)
        print(f"✅ Email sent to {email}")
        # Extract token from the returned magic link
        token = magic_link.split("token=")[-1] if "token=" in str(magic_link) else "unknown_token"
    except ImportError as e:
        print(f"⚠️ shared.email_service not found: {e}")
        # Create test token
        token = f"test_token_{email}"
        print(f"🔗 TEST LINK: https://promptsalchemy.com/auth?token={token}")
    
    # Try to save token (optional)
    try:
        from shared.auth import store_magic_token
        store_magic_token(email, token)
    except ImportError as e:
        print(f"⚠️ shared.auth store function not found: {e}")
    
    return RedirectResponse(f"/check-email?email={email}", status_code=303)

# 3. Auth
@app.get("/auth")
async def auth_callback(token: str):
    print(f"Auth token: {token[:20]}...")
    response = RedirectResponse("/dashboard")
    response.set_cookie(key="session", value=token, httponly=True, secure=True)
    return response


# 4. Dashboard
@app.get("/dashboard")
async def dashboard(request: Request, session: str = Cookie(default=None)):
    if not session:
        return RedirectResponse("/login")
    
    print(f"🔍 DASHBOARD DEBUG: Session token = '{session}'")
    print(f"🔍 DASHBOARD DEBUG: Token starts with 'test_'? {session.startswith('test_')}")
    
    # VERIFY THE SESSION TOKEN TO GET REAL USER EMAIL
    try:
        from shared.auth import verify_magic_link
        # session cookie contains the token
        email = verify_magic_link(session, mark_used=False)
        print(f"🔍 DASHBOARD DEBUG: verify_magic_link returned: '{email}'")
        
        if not email:
            print(f"❌ Invalid or expired token: {session[:20]}...")
            return RedirectResponse("/login")
        print(f"✅ Dashboard loaded for user: {email}")
    except ImportError as e:
        print(f"⚠️ shared.auth not found: {e}, using test email")
        email = "test@example.com"
    
    
    # GET REAL BALANCE FROM DATABASE
    try:
        # Adjust this import based on where your balance function actually is
        from central_bank import get_user_balance
        balance = get_user_balance(email)
        print(f"✅ User balance: {balance} tokens")
    except ImportError as e:
        print(f"⚠️ Balance module not found: {e}")
        balance = 100  # Fallback
    
    # DEBUG: Print apps list
    apps_list = [
        {"name": "Thumbnail Wizard", "cost": 4, "icon": "🖼️", "status": "ready"},
        {"name": "Document Wizard", "cost": 4, "icon": "📄", "status": "ready"},
        {"name": "Hook Wizard", "cost": 4, "icon": "🎣", "status": "ready"},
        {"name": "Prompt Wizard", "cost": 5, "icon": "✨", "status": "ready"},
        {"name": "Script Wizard", "cost": 3, "icon": "📝", "status": "ready"},
        {"name": "A11y Wizard", "cost": 0, "icon": "♿", "status": "ready"},
    ]
    
    print(f"📊 Passing {len(apps_list)} apps to template")
    for app in apps_list:
        print(f"  - {app['name']}")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": email,    # This will be the real email (or test fallback)
        "balance": balance,     # This will be real balance (or 100 fallback)
        "apps": apps_list  # Make sure this variable name matches template
    })

@app.get("/settings")
async def settings(request: Request, session: str = Cookie(default=None)):
    if not session:
        return RedirectResponse("/login")
    
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie(key="session")
    return response

# In clean_app.py, add after /login route:
@app.get("/check-email")
async def check_email(request: Request, email: str):
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email
    })

@app.get("/debug-db")
async def debug_db():
    import os
    import sqlite3
    
    results = []
    
    # Check common Render paths
    paths_to_check = [
        '.',  # Current directory
        'shared',  # In shared folder
        '/opt/render/project/src',  # Render default
        '/var/lib/render/project/src',  # Another Render possibility
        os.path.dirname(os.path.abspath(__file__)),  # Where clean_app.py is
    ]
    
    for path in paths_to_check:
        db_file = os.path.join(path, 'bank.db') if path != '.' else 'bank.db'
        exists = os.path.exists(db_file)
        results.append({
            "path": db_file,
            "exists": exists,
            "size": os.path.getsize(db_file) if exists else 0
        })
    
    # Also try to connect
    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        results.append({"connection": "SUCCESS", "tables": tables})
    except Exception as e:
        results.append({"connection": f"FAILED: {str(e)}"})
    
    return results

def get_db_path():
    """Get the absolute path to bank.db, works both locally and on Render"""
    # Try several possible locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'bank.db'),  # Next to auth.py
        os.path.join(os.getcwd(), 'bank.db'),  # Current working directory
        '/opt/render/project/src/bank.db',  # Render's typical location
        'bank.db',  # Original relative path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found database at: {path}")
            return path
    
    # If not found, use the first location (will create it there)
    default_path = possible_paths[0]
    print(f"⚠️ Database not found, will create at: {default_path}")
    return default_path


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
