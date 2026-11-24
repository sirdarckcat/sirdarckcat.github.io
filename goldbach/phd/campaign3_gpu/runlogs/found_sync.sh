#!/bin/bash
# The lead's ask (23 Nov 19:27Z): copy every card's found lines off the card as they appear, so a hit just before a runtime ends cannot be lost. Every 2 minutes, for each card in
# colab/cards.txt, the lines of all its found files are pulled and kept in found/<card>.jsonl (deduplicated); a new line is printed with a time stamp.
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  for s in $(cat $SP/colab/cards.txt); do
    r=$(c 150 exec -s $s -f $SP/found/peek_found.py --timeout 120)
    echo "$r" | grep -q "^\[fd-end\]" || continue
    echo "$r" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do
      grep -qxF "$line" $SP/found/$s.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$s.jsonl; echo "$(date -u +%FT%TZ) NEW FOUND LINE on $s: ${line:0:300}"; }
    done
  done
  sleep 120
done
