# clean_app.py
from fastapi import FastAPI, Request, Cookie, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os

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
    
    # Generate token
    import secrets
    token = secrets.token_urlsafe(32)
    print(f"🔑 Generated token: {token[:20]}...")
    
    # Try to send email
    try:
        # Adjust based on your email_service module
        from email_service import send_magic_link_email
        send_magic_link_email(email, token)
        print(f"✅ Email sent to {email}")
    except ImportError:
        print(f"⚠️ email_service not found")
        # Show token in console for testing
        print(f"🔗 TEST LINK: https://promptsalchemy.com/auth?token={token}")
    
    # Try to save token (optional)
    try:
        from bank_auth import store_magic_token
        store_magic_token(email, token)
    except ImportError:
        print(f"⚠️ bank_auth not found")
    
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
    
    email = "user@example.com"
    balance = 100
    
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
        "user_email": email,
        "balance": balance,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
