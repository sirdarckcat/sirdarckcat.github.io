#!/usr/bin/env python3
"""bench_ab.py REV [REV ...] [--rounds 5] [--slice 7/1500] [--cc "gcc -O3 -march=native -fopenmp"] [--cpu 2] [--cls 194]

Interleaved timing of two or more revisions of goldbach/fscan on this machine; the first is the reference for the
percentages.  A revision is a git revision (e383cbc, HEAD, origin/branch ...) or WORK for the files in the working tree,
optionally followed by extra compiler flags after an @:  WORK@-DSCORE_MODE=1  WORK@-DFM_GROUPS=3.
A spec that ends in +smt (WORK+smt) is timed while a copy of the same program scans a larger slice on --load, which should be
the other hardware thread of the core of --cpu: it shows how much a thread slows down when its sibling runs the same work.  Each is built from its own copy with a light
timer around scan_vector (TSC cycles a member, vector enumeration excluded) and a checksum over every kept member
(k, n0, rows left), runs `rounds` times alternately on one thread pinned to one CPU, and the script prints the
minimum and the median of each and whether all runs gave identical statistics and checksums.  The minimum is the
number to compare on a shared or noisy machine.  Needs gcc with OpenMP and Python 3; run it on an otherwise idle
core.   Example:  python3 bench_ab.py e383cbc WORK
"""
import argparse, os, re, shlex, statistics, subprocess, sys, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("revs", nargs="+")
ap.add_argument("--rounds", type=int, default=5); ap.add_argument("--slice", default="7/1500")
ap.add_argument("--cc", default="gcc -O3 -march=native -fopenmp -Wno-unused-result -Wno-parentheses")
ap.add_argument("--cpu", default="2"); ap.add_argument("--cls", type=int, default=194)
ap.add_argument("--load", default=None, help="CPU for a background copy of the same program while a spec ending in +smt is timed (the SMT sibling of --cpu)")
args = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
repo = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
rel = os.path.relpath(here, repo)
FILES = ["fscan.c", "fermat52.h", "fermat26.h", "fm_common.h"]       # fm_common.h only exists from the revision that added it

def timer_patch(s):
    s = s.replace("} tls_t;", "    unsigned long long ab_cyc, ab_hash;\n} tls_t;\n#include <x86intrin.h>", 1)
    assert "static void scan_vector(tls_t *T) {" in s, "scan_vector not found"
    s = s.replace("static void scan_vector(tls_t *T) {", "static void scan_vector_(tls_t *T);\nstatic void scan_vector(tls_t *T) { unsigned long long a = __rdtsc(); scan_vector_(T); T->ab_cyc += __rdtsc() - a; }\nstatic void scan_vector_(tls_t *T) {", 1)
    s = s.replace("static void success(tls_t *T, const member_t *m) {", "static inline unsigned long long ab_mix(unsigned long long x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }\nstatic void success(tls_t *T, const member_t *m) {", 1)
    old = "            m->N = (u128)n0 + (u128)k * Mmod; m->k = k; memcpy(m->m, mask, 32);"
    assert old in s, "queue push not found"
    s = s.replace(old, old + "\n            T->ab_hash += ab_mix((k * 0x9E3779B97F4A7C15ULL) ^ ab_mix((n0 + (unsigned long long)a * 977) ^ ab_mix(mask[0] ^ ab_mix(mask[1] ^ ab_mix(mask[2] ^ ab_mix(mask[3]))))));", 1)
    old = "    if (do_hist) {\n        u64 hs[256]"
    assert old in s, "stats tail not found"
    return s.replace(old, '    { unsigned long long c = 0, h = 0; for (int t = 0; t < threads; t++) { c += TT[t]->ab_cyc; h += TT[t]->ab_hash; }\n      printf("AB cycles/member %.4f  hash %016llx\\n", (double)c / (double)total.members, h); }\n' + old, 1)

def build(spec):
    spec = spec.replace("+smt", "")
    rev, _, extra = spec.partition("@")
    d = tempfile.mkdtemp(prefix="bench_ab_")
    for f in FILES:
        if rev == "WORK":
            if not os.path.exists(os.path.join(here, f)): continue
            src = open(os.path.join(here, f)).read()
        else:
            r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{rel}/{f}"], capture_output=True, text=True)
            if r.returncode != 0 and f == "fm_common.h": continue
            if r.returncode != 0: raise SystemExit(f"cannot read {f} at {rev}: {r.stderr}")
            src = r.stdout
        open(os.path.join(d, f), "w").write(timer_patch(src) if f == "fscan.c" else src)
    exe = os.path.join(d, "fscan_ab")
    subprocess.run(shlex.split(args.cc) + shlex.split(extra) + ["-o", exe, os.path.join(d, "fscan.c"), "-lm"], check=True)
    return exe

built = {}
exes = {}
for r in args.revs:
    key = r.replace('+smt', '')
    if key not in built: built[key] = build(key)
    exes[r] = built[key]
th = 99 + args.cls - 194
have_taskset = subprocess.run(["which", "taskset"], capture_output=True).returncode == 0
def mkcmd(e, cpu, sl):
    return (["taskset", "-c", cpu] if have_taskset else []) + [e, "10007", "383", str(args.cls), str(args.cls), "4e18", "1e23", str(th), "113", f"rref={args.cls}", f"slice={sl}", "threads=1"]
cmd = lambda e: mkcmd(e, args.cpu, args.slice)
load_cmd = lambda e: mkcmd(e, args.load, "1/40")               # a different slice, about 5 times more work than the timed one: it scans for the whole run
res = {k: [] for k in exes}; sig = {k: set() for k in exes}
import time
for r in range(args.rounds):
    for k, e in exes.items():
        bg = None
        if k.endswith("+smt"):
            if not args.load: raise SystemExit("+smt needs --load CPU")
            bg = subprocess.Popen(load_cmd(e), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(6)                                      # let it finish its vector enumeration and start scanning
        out = subprocess.run(cmd(e), capture_output=True, text=True).stdout
        if bg: bg.terminate(); bg.wait()
        c = float(re.search(r"AB cycles/member ([\d.]+)", out).group(1)); h = re.search(r"hash (\w+)", out).group(1)
        st = re.search(r"vectors=(\d+) members=(\d+) selected=(\d+) kept=(\d+) tests=(\d+) prps=(\d+) found=(\d+)", out).groups()
        res[k].append(c); sig[k].add((h,) + st)
        print(f"round {r+1}/{args.rounds} {k:>24s}: {c:.3f} cycles/member", flush=True)
print()
base = None
for k in exes:
    m = min(res[k]); base = base or m
    print(f"{k:>24s}: min {m:6.3f}  median {statistics.median(res[k]):6.3f}  ({100 * (m / base - 1):+.1f}% vs {args.revs[0]}, TSC cycles per member, whole scan_vector)")
allsig = set().union(*sig.values())
print("statistics and kept-member checksum IDENTICAL in all runs" if len(allsig) == 1 else f"MISMATCH between runs: {allsig}")
sys.exit(0 if len(allsig) == 1 else 1)
