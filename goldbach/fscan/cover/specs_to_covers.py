#!/usr/bin/env python3
"""Spec files (JSON) -> cover lines "COVER k r:a r:a ..." on stdout, the moduli in increasing order: starting
points for covergen from any delivered spec file.

    python3 specs_to_covers.py specs.json [more.json ...] > start.txt
"""
import json, sys
for f in sys.argv[1:]:
    for s in json.load(open(f)):
        print("COVER", len(s["residual"]), " ".join(f"{r}:{a}" for r, a in sorted(map(tuple, s["cover"]))))
