"""
One-time script: opens browser, asks you to authorize Google Drive access,
saves the refresh token to token.json for use by scrape_local.py
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)

token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes),
}
with open("token.json", "w") as f:
    json.dump(token_data, f, indent=2)

print("token.json guardado. Ya puedes correr scrape_local.py")
