#!/usr/bin/env python3
"""Restart-proof OAuth for the Colab CLI.

The CLI's built-in InstalledAppFlow holds PKCE state in process memory,
which does not survive this environment's container restarts. This
helper persists the PKCE verifier to disk so the URL can be issued and
the code exchanged in different processes (or different containers).

  auth_pkce.py start     -> prints auth URL (verifier saved to disk)
  auth_pkce.py exchange CODE -> writes ~/.config/colab-cli/token.json

Client id/secret are the public Google Cloud SDK installed-app
constants that ship in every gcloud release (not secrets).
"""

import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.parse
import urllib.request

CLIENT_ID = "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
CLIENT_SECRET = "d-FL95Q19q7MQmFpd7hHD0Ty"
REDIRECT = "https://sdk.cloud.google.com/applicationdefaultauthcode.html"
SCOPES = ("openid https://www.googleapis.com/auth/userinfo.profile "
          "https://www.googleapis.com/auth/userinfo.email "
          "https://www.googleapis.com/auth/cloud-platform "
          "https://www.googleapis.com/auth/colaboratory "
          "https://www.googleapis.com/auth/drive.file")
VERIFIER_PATHS = [
    os.path.expanduser("~/.colab_pkce_verifier"),
    "/home/user/sirdarckcat.github.io/.git/colab_pkce_verifier",
]
TOKEN_PATH = os.path.expanduser("~/.config/colab-cli/token.json")


def start():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    for p in VERIFIER_PATHS:
        try:
            with open(p, "w") as f:
                f.write(verifier)
        except OSError:
            pass
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    params = {
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT, "scope": SCOPES,
        "code_challenge": challenge, "code_challenge_method": "S256",
        "prompt": "consent", "access_type": "offline",
    }
    print("https://accounts.google.com/o/oauth2/auth?"
          + urllib.parse.urlencode(params))


def exchange(code):
    verifier = None
    for p in VERIFIER_PATHS:
        try:
            verifier = open(p).read().strip()
            break
        except OSError:
            continue
    assert verifier, "no persisted verifier found — rerun start"
    data = urllib.parse.urlencode({
        "code": code, "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT,
        "grant_type": "authorization_code", "code_verifier": verifier,
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    tok = json.loads(urllib.request.urlopen(req).read())
    cred = {
        "token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "scopes": SCOPES.split(), "type": "authorized_user",
        "universe_domain": "googleapis.com", "account": "",
    }
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(cred, f)
    print("token written to", TOKEN_PATH)


if __name__ == "__main__":
    if sys.argv[1] == "start":
        start()
    else:
        exchange(sys.argv[2])
