#!/usr/bin/env python3
"""Cut a spec into consecutive k slices (search.py prints one summary line per spec, so a slice is the progress unit).
    python3 slices.py spec.json name nslices blocks_per_slice ceiling_digits out.json"""
import json, sys
spec, name, n, bps, ceil, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
s = json.load(open(spec))
step = bps * 32768
specs = []
for i in range(n):
    t = dict(s)
    t.update(name=f"{name}_s{i:03d}", kstart=i * step, kmax=(i + 1) * step, ceiling_digits=ceil)
    specs.append(t)
json.dump(specs, open(out, "w"))
print(f"{n} slices of {step} members, k < {n * step}")
