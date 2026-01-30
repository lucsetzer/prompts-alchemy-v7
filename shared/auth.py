import os
import sqlite3
from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "your-secret-key-change-in-production"
serializer = URLSafeTimedSerializer(SECRET_KEY)

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

def verify_magic_link(token: str, max_age=900, mark_used=True):
    """Verify magic link token"""
    
    if token.startswith("test_"):
        return token[5:]  # Return email after "test_"
    
    print(f"🔍 VERIFY DEBUG: Checking token {token[:30]}...")
    
    try:
        email = serializer.loads(token, salt="magic-link", max_age=max_age)
        print(f"🔍 VERIFY DEBUG: Token valid for {email}")
        
        # USE THE SHARED FUNCTION
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        
        c = conn.cursor()
        c.execute("SELECT used FROM magic_links WHERE token = ?", (token,))
        result = c.fetchone()
        
        if not result:
            print(f"🔍 VERIFY DEBUG: Token not found in database!")
            return None
            
        if result[0]:  # Already used
            print(f"🔍 VERIFY DEBUG: Token already used")
            return None
            
        # Only mark as used if requested
        if mark_used:
            c.execute("UPDATE magic_links SET used = TRUE WHERE token = ?", (token,))
            conn.commit()
            print(f"🔍 VERIFY DEBUG: Marked token as used")
        
        conn.close()
        print(f"🔍 VERIFY DEBUG: SUCCESS! Login for {email}")
        return email
        
    except Exception as e:
        print(f"🔍 VERIFY DEBUG: Error: {type(e).__name__}: {e}")
        return None
    return token
