# This card's near_events.jsonl lines (each one in full) and its found.jsonl line count.
import os
C = "/content/c170r"
p = os.path.join(C, "near_events.jsonl")
if os.path.exists(p):
    for l in open(p):
        if l.strip():
            print("[ne] " + l.strip())
print("[ne] FOUNDLINES %d" % sum(1 for l in open(os.path.join(C, "found.jsonl")) if l.strip()) if os.path.exists(os.path.join(C, "found.jsonl")) else "[ne] FOUNDLINES 0")
