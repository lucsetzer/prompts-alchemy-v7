import os
import resend
from bank_auth import create_magic_link
from dotenv import load_dotenv

load_dotenv()

print(f"DEBUG: Loading .env from {os.path.abspath('.env')}")
print(f"DEBUG: RESEND_API_KEY = {'SET' if os.getenv('RESEND_API_KEY') else 'NOT SET'}")

from bank_auth import create_magic_link

def send_magic_link_email(email: str, token: str):
    """Send magic link email via Resend.com"""
    
    # Get your Render URL for the magic link
    public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
    magic_link = f"{public_url}/auth?token={token}"
    
    # Get Resend API key
    api_key = os.getenv("RESEND_API_KEY")
    
    if not api_key:
        print("❌ RESEND_API_KEY not set. Using mock mode.")
        print(f"📨 MOCK: Magic link for {email}: {magic_link}")
        return "mock_no_api_key"
    
    # Configure Resend
    resend.api_key = api_key
    
    try:
        # Send real email - CHANGE FROM EMAIL TO YOUR VERIFIED DOMAIN
        params = {
            "from": "onboarding@resend.dev",  # ← CHANGE THIS TO YOUR VERIFIED DOMAIN
            "to": [email],
            "subject": "Your Magic Login Link - Prompts Alchemy",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #0cc0df;">Your Magic Login Link</h2>
                <p>Click the link below to login to your Prompts Alchemy account:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_link}" 
                       style="background: #0cc0df; color: white; padding: 14px 28px; 
                              text-decoration: none; border-radius: 8px; font-weight: bold;
                              display: inline-block; font-size: 16px;">
                        Login to Prompts Alchemy
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Or copy this link:<br>
                    <code style="background: #f5f5f5; padding: 8px; border-radius: 4px; 
                          word-break: break-all; display: block; margin: 10px 0;">
                        {magic_link}
                    </code>
                </p>
                
                <p style="color: #888; font-size: 12px; border-top: 1px solid #eee; padding-top: 15px;">
                    This link will expire in 15 minutes.<br>
                    If you didn't request this login, please ignore this email.
                </p>
            </div>
            """
        }
        
        response = resend.Emails.send(params)
        print(f"✅ Real email sent to {email}, ID: {response['id']}")
        return response
        
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        # Fallback to console for debugging
        print(f"📨 FALLBACK: Magic link for {email}: {magic_link}")
        return f"error: {str(e)}"
