from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import secrets
from datetime import datetime, timedelta

app = FastAPI()

# Bank database setup
def init_bank():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (email TEXT PRIMARY KEY, tokens INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id TEXT, email TEXT, amount INTEGER, description TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_bank()

class Deposit(BaseModel):
    email: str
    tokens: int
    payment_id: str  # From Stripe

class SpendRequest(BaseModel):
    email: str
    app_id: str
    tokens: int
    description: str

@app.post("/deposit")
def deposit_funds(deposit: Deposit):
    """When user buys tokens via Stripe"""
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    
    # Add to balance
    c.execute('INSERT OR IGNORE INTO accounts (email, tokens) VALUES (?, 0)', (deposit.email,))
    c.execute('UPDATE accounts SET tokens = tokens + ? WHERE email = ?', 
              (deposit.tokens, deposit.email))
    
    # Record transaction
    tx_id = secrets.token_hex(8)
    c.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?)',
              (tx_id, deposit.email, deposit.tokens, 
               f"Purchase via {deposit.payment_id}", datetime.utcnow()))
    
    conn.commit()
    conn.close()
    return {"status": "deposited", "new_balance": get_balance(deposit.email)}

@app.post("/spend")
def spend_tokens(spend: SpendRequest):
    """When an AI app uses tokens"""
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    
    # Check balance
    c.execute('SELECT tokens FROM accounts WHERE email = ?', (spend.email,))
    result = c.fetchone()
    if not result or result[0] < spend.tokens:
        raise HTTPException(status_code=402, detail="Insufficient tokens")
    
    # Deduct
    c.execute('UPDATE accounts SET tokens = tokens - ? WHERE email = ?',
              (spend.tokens, spend.email))
    
    # Record spend
    tx_id = secrets.token_hex(8)
    c.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?)',
              (tx_id, spend.email, -spend.tokens, 
               f"{spend.app_id}: {spend.description}", datetime.utcnow()))
    
    conn.commit()
    conn.close()
    return {"status": "spent", "remaining": get_balance(spend.email)}

def get_balance(email: str) -> int:
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('SELECT tokens FROM accounts WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

@app.get("/test")
def test():
    return {"status": "bank is working"}

@app.get("/")
def root():
    return {"message": "AI Wizards Bank API", "docs": "/docs"}