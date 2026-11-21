#!/usr/bin/env python3
"""One-time local OAuth helper to mint a GDRIVE_REFRESH_TOKEN for Vocl analytics uploads."""
from __future__ import annotations

import os
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from dotenv import load_dotenv

load_dotenv()

REDIRECT_URI = "http://localhost:8765/"
SCOPE = "https://www.googleapis.com/auth/drive.file"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


def main() -> None:
    client_id = (os.environ.get("GDRIVE_CLIENT_ID") or os.environ.get("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (os.environ.get("GDRIVE_CLIENT_SECRET") or "").strip()
    if not client_id:
        client_id = input("Google OAuth Client ID: ").strip()
    if not client_secret:
        client_secret = input("Google OAuth Client Secret: ").strip()

    auth_code: dict[str, str] = {}

    class _CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if "code" in params:
                auth_code["code"] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>Vocl Drive Auth Complete</h2><p>You can close this tab and return to the terminal.</p>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing authorization code.")

        def log_message(self, _format: str, *_args: object) -> None:
            return

    auth_url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    })

    print(f"\nOpening browser for Google Drive authorization:\n{auth_url}\n")
    server = HTTPServer(("127.0.0.1", 8765), _CallbackHandler)
    webbrowser.open(auth_url)
    server.handle_request()
    server.server_close()

    code = auth_code.get("code")
    if not code:
        raise SystemExit("Authorization cancelled or failed (no code received).")

    resp = httpx.post(
        TOKEN_ENDPOINT,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=20.0,
    )
    resp.raise_for_status()
    tokens = resp.json()
    refresh_token = tokens.get("refresh_token", "")
    if not refresh_token:
        raise SystemExit(f"No refresh_token returned: {tokens}")

    print("\nAdd these to your .env and Hugging Face Space Secrets:")
    print(f"GDRIVE_CLIENT_ID={client_id}")
    print(f"GDRIVE_CLIENT_SECRET={client_secret}")
    print(f"GDRIVE_REFRESH_TOKEN={refresh_token}")
    print("GDRIVE_FOLDER_ID=<your-drive-folder-id>")


if __name__ == "__main__":
    main()
