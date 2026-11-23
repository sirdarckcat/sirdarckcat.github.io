#!/usr/bin/env python3
"""Spec files or pool files (JSON) -> cover lines "COVER k r:a r:a ..." on stdout, the moduli in increasing order:
starting points for covergen from any delivered file.

    python3 specs_to_covers.py file.json [more.json ...] > start.txt

A spec file is a list of specs (campaign3 format: "cover" as [r, a] pairs, "residual").  A pool file (the format of
goldbach/phd/cap200) is {"Q": ..., "mods": [r, ...], "pool": [[rows, [a, ...]], ...]}.
"""
import json, sys

def covers_of(path):
    d = json.load(open(path))
    if isinstance(d, dict) and "pool" in d:
        for k, classes in d["pool"]:
            yield k, sorted(zip(d["mods"], classes))
    else:
        for s in d:
            yield len(s["residual"]), sorted(map(tuple, s["cover"]))

if __name__ == "__main__":
    for f in sys.argv[1:]:
        for k, cov in covers_of(f):
            print("COVER", k, " ".join(f"{r}:{a}" for r, a in cov))
