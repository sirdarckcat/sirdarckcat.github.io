#!/usr/bin/env python3
"""Keep the covergen lines of this card's share: md5 of the residue list mod NPART == PART (the three RTX cards never get the same vector).
    python3 part.py walk.txt PART NPART > walk.part"""
import hashlib, sys
part, npart = int(sys.argv[2]), int(sys.argv[3])
for line in open(sys.argv[1]):
    f = line.split(None, 2)
    if len(f) == 3 and f[0] == "COVER" and int(hashlib.md5(f[2].strip().encode()).hexdigest(), 16) % npart == part:
        sys.stdout.write(line)
