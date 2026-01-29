from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import auth modules
sys.path.append(str(Path(__file__).parent.parent))

template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# Import from root directory
try:
    from bank_auth import verify_magic_link, create_magic_link
    from email_service import send_magic_link_email
except ImportError as e:
    print(f"Import error: {e}")
    # Mock functions for testing
    def verify_magic_link(token):
        return "test@example.com" if token else None
    def create_magic_link(email):
        return f"/auth?token=test_{email}"
    def send_magic_link_email(email):
        print(f"📨 MOCK: Magic link for {email}")
        return f"http://localhost:8000/auth?token=test_{email}"

app = FastAPI()

def get_user_balance(email: str):
    """Get user's token balance from bank database, create if doesn't exist"""
    db_path = Path(__file__).parent.parent / "bank.db"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    
    # Check if exists
    c.execute('SELECT tokens FROM accounts WHERE email = ?', (email,))
    result = c.fetchone()
    
    if result:
        balance = result[0]
    else:
        # Create new account with 0 tokens
        c.execute('INSERT INTO accounts (email, tokens) VALUES (?, ?)', (email, 0))
        conn.commit()
        balance = 0
        print(f"Created new account for {email}")
    
    conn.close()
    return balance

print(f"🚨 LOADED: {__file__}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
