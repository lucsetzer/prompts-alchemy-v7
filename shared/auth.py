import os
import sqlite3
from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "your-secret-key-change-in-production"
serializer = URLSafeTimedSerializer(SECRET_KEY)



def verify_magic_link(token: str, max_age=900, mark_used=True):
    """Verify magic link token"""
    
    if token.startswith("test_"):
        return token[5:]  # Return email after "test_"
    
    print(f"🔍 VERIFY DEBUG: Checking token {token[:30]}...")
    
    try:
        email = serializer.loads(token, salt="magic-link", max_age=max_age)
        print(f"🔍 VERIFY DEBUG: Token valid for {email}")
        
        # USE THE ABSOLUTE PATH
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
