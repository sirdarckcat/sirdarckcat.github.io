#!/bin/bash
# Self-restoring Colab toolchain: run after any container restart.
set -e
export PATH="$HOME/.local/bin:$PATH"
command -v colab >/dev/null 2>&1 || {
  pip install -q uv 2>/dev/null | tail -0
  uv tool install -q google-colab-cli --python 3.12
}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/baa8b498-20b7-5e39-a641-6ce05571c44f/scratchpad
if [ ! -f ~/.config/colab-cli/token.json ]; then
  if [ -n "$COLAB_REFRESH_TOKEN" ]; then
    # durable path: refresh token injected as an environment secret
    mkdir -p ~/.config/colab-cli
    python3 - <<'PY'
import json, os
json.dump({
  "token": None, "refresh_token": os.environ["COLAB_REFRESH_TOKEN"],
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
  "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
  "scopes": ["https://www.googleapis.com/auth/colaboratory",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/cloud-platform"],
  "type": "authorized_user", "universe_domain": "googleapis.com",
  "account": "",
}, open(os.path.expanduser("~/.config/colab-cli/token.json"), "w"))
print("token minted from COLAB_REFRESH_TOKEN")
PY
  else
    for src in $SP/colab_token_backup.json /home/user/sirdarckcat.github.io/.git/colab_token_backup.json; do
      [ -f "$src" ] && mkdir -p ~/.config/colab-cli && cp "$src" ~/.config/colab-cli/token.json && break
    done
  fi
fi
colab sessions < /dev/null 2>&1 | tail -3
