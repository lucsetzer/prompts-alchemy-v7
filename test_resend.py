import os
import resend

resend.api_key = "re_NWmbEJ4P_ByDvS1NGLSfVCqmtavbpreaa"  # Your actual key

try:
    r = resend.Emails.send({
        "from": "noreply@promptsalchemy.com",
        "to": ["lucsetzer@gmail.com"],  # Your real email
        "subject": "Resend Test",
        "html": "<p>Testing Resend</p>"
    })
    print(f"✅ Success: {r}")
except Exception as e:
    print(f"❌ Error: {e}")