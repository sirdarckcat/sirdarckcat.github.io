#!/bin/bash
# Self-restoring Colab toolchain: run after any container restart.
set -e
export PATH="$HOME/.local/bin:$PATH"
command -v colab >/dev/null 2>&1 || {
  pip install -q uv 2>/dev/null | tail -0
  uv tool install -q google-colab-cli --python 3.12
}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/baa8b498-20b7-5e39-a641-6ce05571c44f/scratchpad
[ -f ~/.config/colab-cli/token.json ] || {
  for src in $SP/colab_token_backup.json /home/user/sirdarckcat.github.io/.git/colab_token_backup.json; do
    [ -f "$src" ] && mkdir -p ~/.config/colab-cli && cp "$src" ~/.config/colab-cli/token.json && break
  done
}
colab sessions 2>&1 | tail -3
