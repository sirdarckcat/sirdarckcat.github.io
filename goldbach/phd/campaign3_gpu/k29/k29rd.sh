#!/bin/bash
# 29-bit kernel on this RTX card: /content/f29 (a copy of /content/f28w with 710585f's fermat661/cuda over it), the vector-mode identity check and known case
# (k29v.sh: the campaign paused meanwhile), then deploy_k29r.py (deploys only if that check passed).
[ -f /content/f29/fermat29_step_s1.cuh ] || { [ -d /content/f29 ] || cp -a /content/f28w /content/f29; tar -xzf /content/f29_overlay.tgz -C /content/f29; }
bash /content/k29v.sh
python3 /content/deploy_k29r.py
echo K29RD-DONE
