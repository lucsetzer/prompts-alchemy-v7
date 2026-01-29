from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

# MANUAL IMPORTS - bypass module system
import sys
sys.path.append('.')  # Current directory

# Import auth functions directly
import auth
import email_service

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")

@app.get("/")
async def root(request: Request, session: str = Cookie(default=None)):
    if not session:
        return RedirectResponse("/login")
    
    email = auth.verify_magic_link(session)
    if not email:
        return RedirectResponse("/login")
    
    # Get balance
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('SELECT tokens FROM accounts WHERE email = ?', (email,))
    result = c.fetchone()
    balance = result[0] if result else 0
    conn.close()
    
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

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_request(email: str = Form(...)):
    email_service.send_magic_link_email(email)
    return RedirectResponse(f"/check-email?email={email}")

@app.get("/check-email")
async def check_email_page(request: Request, email: str):
    return templates.TemplateResponse("check_email.html", {"request": request, "email": email})

@app.get("/auth")
async def auth_callback(token: str):
    email = auth.verify_magic_link(token)
    if not email:
        return RedirectResponse("/login?error=invalid")
    
    response = RedirectResponse("/")
    response.set_cookie(key="session", value=token)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse("/login")
    response.delete_cookie(key="session")
    return response

print(f"🚨 LOADED: {__file__}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
