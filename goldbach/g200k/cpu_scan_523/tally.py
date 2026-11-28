#!/usr/bin/env python3
"""Tally the 200-digit side scan of the 523 family from its worker logs (search_c.py summary lines, one per cover).

    python3 tally.py [logs]          default: the logs/ directory next to this file

Prints covers (each counted once, by name), the cover range and whether it is contiguous, members, Fermat tests, core-hours,
finds, and the expected number of finds as research's tally computes it: the sum over covers of K * e^-E^ * hit%, where K is the
cover's member count, E^ the mean number of probable primes a member would have among its surviving rows, and hit% the share of
the cover's success probability that the tested 1.5% held.  (A Gaussian correction for the spread of the survivor counts puts
this formula about 1.5 times too high; it is kept for comparison with research's ledger.)  famB_rescan_* logs are reported
separately: they are rescans of covers the GPU fleet already used, not new coverage."""
import glob, math, os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
pat = re.compile(r"^\[(c\d+)_r(\d+)\] k=\[(\d+),(\d+)\) (\d+)s .* tests=(\d+) prp=(\d+) p\^=([\d.]+) alive/k=([\d.]+) "
                 r"E\^=([\d.]+) hit%=([\d.]+) found=(\d+)")


def tally(files):
    seen = {}
    for f in sorted(files):
        for line in open(f):
            m = pat.match(line)
            if not m or m.group(1) in seen:
                continue
            k0, k1, secs, tests = (int(m.group(i)) for i in (3, 4, 5, 6))
            seen[m.group(1)] = dict(rows=int(m.group(2)), members=k1 - k0, secs=secs, tests=tests, found=int(m.group(12)),
                                    expected=(k1 - k0) * math.exp(-float(m.group(10))) * float(m.group(11)) / 100)
    return seen


def report(label, t):
    if not t:
        print(f"{label}: no summary lines")
        return
    ids = sorted(int(n[1:]) for n in t)
    contiguous = ids == list(range(ids[0], ids[-1] + 1))
    s = lambda key: sum(v[key] for v in t.values())
    print(f"{label}: {len(t)} covers, c{ids[0]:04d}..c{ids[-1]:04d} ({'contiguous' if contiguous else 'NOT contiguous'}), "
          f"rows {min(v['rows'] for v in t.values())}-{max(v['rows'] for v in t.values())}, members {s('members'):.4g}, "
          f"Fermat tests {s('tests'):.4g}, {s('secs') / 3600:.1f} core-hours, found {s('found')}, expected {s('expected'):.5f}")


logs = glob.glob(os.path.join(d, "*.log"))
report("523 family", tally([f for f in logs if not os.path.basename(f).startswith("famB")]))
report("family B rescans", tally([f for f in logs if os.path.basename(f).startswith("famB")]))
