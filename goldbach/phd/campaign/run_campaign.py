"""Restart-safe driver for the E10 campaign.

Reads specs_variants.json, drops every spec already completed according to
search.log ("[name] k=[...] ..." summary lines) and relaunches search.py on
the remainder, appending to the same log.  Idempotent: safe to run after any
container restart; exits immediately if a hit is already recorded or nothing
remains.
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
SPECS = os.path.join(HERE, "specs_variants.json")
LOG = os.path.join(HERE, "search.log")
FOUND = os.path.join(HERE, "found.jsonl")
REMAINING = os.path.join(HERE, "remaining.json")


def main():
    if os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
        print("hit already recorded in found.jsonl; not relaunching")
        return 1
    specs = json.load(open(SPECS))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    remaining = [s for s in specs if s["name"] not in done]
    print(f"{len(specs)} specs total, {len(done)} completed, "
          f"{len(remaining)} remaining")
    if not remaining:
        print("campaign budget exhausted with no hit")
        return 2
    json.dump(remaining, open(REMAINING, "w"))
    with open(LOG, "a") as log:
        subprocess.Popen(
            [sys.executable, os.path.join(GOLDBACH, "search.py"), REMAINING,
             "--procs", "4", "--out", FOUND],
            cwd=GOLDBACH, stdout=log, stderr=log,
            start_new_session=True)
    print("relaunched search.py on remaining specs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
