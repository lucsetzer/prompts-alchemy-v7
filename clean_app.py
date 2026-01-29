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
    print(f"Login: {email}")
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
    
    # Mock user
    email = "user@example.com"
    balance = 100
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": email,
        "balance": balance,
        "apps": [
            {"name": "Thumbnail", "cost": 4, "icon": "🖼️"},
            {"name": "Document", "cost": 4, "icon": "📄"},
            {"name": "Hook", "cost": 4, "icon": "🎣"},
            {"name": "Prompt", "cost": 5, "icon": "✨"},
            {"name": "Script", "cost": 3, "icon": "📝"},
            {"name": "A11y", "cost": 0, "icon": "♿"},
        ]
    })

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
