#!/usr/bin/env python3
"""What a given closeness costs at each size of N.

For a size (digits of N) and a target fraction c of the ceiling, take Q = c * ceiling, the odd primes whose product
leaves about K members per residue vector as moduli, find the best cover with ptcover, and print the search exponent
E = k * boost / ln N and the number of candidates per success, e^(E (1 + p/2)).  The ceilings are those of
goldbach/closeness.py (the largest g expected below N).

    python3 closeness_cost.py            # needs ./ptcover and betas56.txt; about two minutes
"""
import math, subprocess, tempfile, os
CASES = [  # digits, fraction of the ceiling, ceiling, members per vector
    (23, 0.50, 16188, 1e6), (23, 0.75, 16188, 1e6), (23, 0.90, 16188, 1e6), (30, 0.50, 30294, 1e6), (30, 0.75, 30294, 1e6),
    (40, 0.50, 58996, 1e7), (50, 0.50, 98250, 1e8), (60, 0.50, 148547, 1e8), (100, 0.50, 465348, 1e9),
    (200, 0.10, 2130704, 5e9), (200, 0.50, 2130704, 5e9)]
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
P = primes_upto(3000)
here = os.path.dirname(os.path.abspath(__file__))
print("| digits | target | Q | rows | moduli | random | best cover | E (nats) | candidates per success |")
print("|---|---|---|---|---|---|---|---|---|")
for d, c, ceil, K in CASES:
    Q = int(c * ceil); budget = d * math.log(10) - math.log(K)
    mods = []; s = math.log(2)
    for p in P[1:]:
        if s + math.log(p) > budget: break
        s += math.log(p); mods.append(p)
    boost = 2.0
    for p in mods: boost *= p / (p - 1)
    with tempfile.NamedTemporaryFile("w", suffix=".mod", delete=False) as f:
        f.write("".join(f"{p}\n" for p in mods)); name = f.name
    sweeps = 12000 if d <= 60 else (6000 if d == 100 else (8000 if c < 0.3 else 2500))
    out = subprocess.run([os.path.join(here, "ptcover"), str(Q), name, str(sweeps), "5", os.path.join(here, "betas56.txt")],
                         capture_output=True, text=True).stdout
    os.unlink(name)
    lines = [l for l in out.splitlines() if l and l[0] != "B"]
    rows = int(lines[0].split("rows=")[1].split()[0]); rnd = float(lines[2].split()[1])
    best = int([l for l in lines if "best k" in l][0].split(":")[1])
    p1 = boost / (d * math.log(10)); E = best * p1
    print(f"| {d} | {int(100*c)}% | {Q:,} | {rows:,} | {len(mods)} (to {mods[-1]}) | {rnd:,.0f} | {best:,} | {E:.1f} | {math.exp(E * (1 + p1 / 2)):.1e} |", flush=True)
