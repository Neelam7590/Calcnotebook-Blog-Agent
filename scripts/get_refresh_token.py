"""
Ek baar chalao: browser khulega, Google account se login karo,
terminal mein GOOGLE_REFRESH_TOKEN print hoga. Use .env aur GitHub Secrets mein daalo.

Run:  python scripts/get_refresh_token.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCOPES = ["https://www.googleapis.com/auth/blogger"]

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
if not client_id or not client_secret:
    raise SystemExit("Pehle .env mein GOOGLE_CLIENT_ID aur GOOGLE_CLIENT_SECRET bharo.")

config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(config, SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

print("\n=== Ye apna GOOGLE_REFRESH_TOKEN hai ===")
print(creds.refresh_token)
print("=========================================")
print(".env mein GOOGLE_REFRESH_TOKEN=... ke saath daalo, aur GitHub Secrets mein bhi.")
