"""
One-time OAuth 2.0 token generator for LinkedIn.
Run this locally to get your access token and refresh token.

Usage:
    python auth/get_token.py

You will need your LinkedIn app's Client ID and Client Secret.
"""

import http.server
import urllib.parse
import webbrowser
import requests
import sys
import os


# LinkedIn OAuth URLs
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI = "http://localhost:8585/callback"
SCOPES = "openid profile email w_member_social"


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle the OAuth callback from LinkedIn."""

    auth_code = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authorization successful!</h1>"
                b"<p>You can close this window now.</p></body></html>"
            )
        elif "error" in params:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            error = params.get("error_description", params["error"])[0]
            self.wfile.write(
                f"<html><body><h1>Error</h1><p>{error}</p></body></html>".encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default logging


def main():
    print("=" * 60)
    print("  LinkedIn OAuth Token Generator")
    print("=" * 60)

    client_id = input("\nEnter your LinkedIn Client ID: ").strip()
    client_secret = input("Enter your LinkedIn Client Secret: ").strip()

    if not client_id or not client_secret:
        print("[!] Client ID and Secret are required.")
        sys.exit(1)

    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "linkedin_auto_poster_auth",
    }
    auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    print(f"\n[1] Opening browser for LinkedIn authorization...")
    print(f"    If it doesn't open, visit: {auth_link}\n")
    webbrowser.open(auth_link)

    # Start local server to catch the callback
    print("[2] Waiting for authorization callback on http://localhost:8585 ...")
    server = http.server.HTTPServer(("localhost", 8585), OAuthCallbackHandler)
    server.handle_request()  # Handle one request
    server.server_close()

    if not OAuthCallbackHandler.auth_code:
        print("[!] No authorization code received. Exiting.")
        sys.exit(1)

    print(f"\n[3] Got authorization code! Exchanging for tokens...")

    # Exchange code for tokens
    try:
        resp = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": OAuthCallbackHandler.auth_code,
                "redirect_uri": REDIRECT_URI,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
        )
        resp.raise_for_status()
        tokens = resp.json()
    except Exception as e:
        print(f"[!] Failed to exchange code for tokens: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"    Response: {e.response.text}")
        sys.exit(1)

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    expires_in = tokens.get("expires_in", 0)

    print("\n" + "=" * 60)
    print("  TOKENS GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n  Access Token (expires in {expires_in // 86400} days):")
    print(f"  {access_token[:20]}...{access_token[-10:]}")
    print(f"\n  Refresh Token:")
    print(f"  {refresh_token[:20]}...{refresh_token[-10:]}" if refresh_token else "  (none)")

    print("\n" + "=" * 60)
    print("  STORE THESE AS GITHUB SECRETS:")
    print("=" * 60)
    print(f"\n  LINKEDIN_ACCESS_TOKEN = {access_token}")
    print(f"  LINKEDIN_REFRESH_TOKEN = {refresh_token}")
    print(f"  LINKEDIN_CLIENT_ID = {client_id}")
    print(f"  LINKEDIN_CLIENT_SECRET = {client_secret}")

    print(f"\n  Go to: https://github.com/YOUR_REPO/settings/secrets/actions")
    print(f"  Add each secret above.\n")

    # Save locally for testing
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    with open(env_path, "w") as f:
        f.write(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
        f.write(f"LINKEDIN_REFRESH_TOKEN={refresh_token}\n")
        f.write(f"LINKEDIN_CLIENT_ID={client_id}\n")
        f.write(f"LINKEDIN_CLIENT_SECRET={client_secret}\n")
    print(f"  [+] Also saved to .env file for local testing.")
    print(f"  [!] DO NOT commit .env to git!\n")


if __name__ == "__main__":
    main()