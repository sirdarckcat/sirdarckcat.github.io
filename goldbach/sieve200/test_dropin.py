#!/usr/bin/env python3
"""search_c.py against search.py: run_block on the same blocks must return the same six numbers (successes, tests, prps,
alive_total, hm_kept, hm_all), and the command lines must print the same log line (apart from time and rate) and write the
same found file.

    python3 test_dropin.py [--full]      # --full adds a whole campaign3 block (about 20 s)
"""
import argparse
import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, GB)


def load_ref():
    """search.py again, as its own module with its own G, before search_c patches the first copy."""
    loader = importlib.machinery.SourceFileLoader("search_ref", os.path.join(GB, "search.py"))
    spec = importlib.util.spec_from_loader("search_ref", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


ref = load_ref()
import search_c  # noqa: E402  (patches search.py's functions in the *other* copy of the module)

CAMPAIGN = os.path.join(GB, "phd", "campaign3", "base_spec.json")
SMALL = os.path.join(GB, "tscan", "q10007_e23.json")


def run_both(spec, sieve_b, L, ks, flags):
    ref.G.clear()
    ref.init_spec(spec, sieve_b, L)
    ref.G.update(flags)
    outs_ref = [ref.run_block(k0) for k0 in ks]
    search_c.init_spec(spec, sieve_b, L)
    search_c.G.update(flags)
    outs_c = [search_c.run_block(k0) for k0 in ks]
    return outs_ref, outs_c


def compare(name, spec, sieve_b, L, ks, flags):
    a, b = run_both(spec, sieve_b, L, ks, flags)
    ok = a == b
    ns = sum(len(x[0]) for x in a)
    nt = sum(x[1] for x in a)
    npr = sum(x[2] for x in a)
    print(f"  {name:<46s} L={L:<6d} {len(ks)} blocks  successes={ns} tests={nt} prps={npr}  {'identical' if ok else 'DIFFERENT'}",
          flush=True)
    if not ok:
        for x, y in zip(a, b):
            if x != y:
                print("   ref:", x[:1], x[1:], "\n   c:  ", y[:1], y[1:])
                break
    return ok


def normalize(line):
    return re.sub(r" \d+s \(\d+ k/s\)", " <time>", line.strip())


def cli(script, specfile, extra, out):
    r = subprocess.run([sys.executable, script, specfile, "--out", out] + extra, capture_output=True, text=True, cwd=GB)
    if r.returncode:
        print(r.stderr[-2000:])
    return [normalize(x) for x in r.stdout.splitlines() if x.strip()], (open(out).read() if os.path.exists(out) else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    ok = True
    small = json.load(open(SMALL))
    camp = json.load(open(CAMPAIGN))
    print("run_block, the six returned numbers")
    for rows in (14, 40):
        sp = dict(small)
        sp["residual"] = small["residual"][:rows]                  # few rows: many members are successes
        for flags in ({}, {"sort_tests": True}, {"skip_frac": 0.9, "p_est": 0.3}, {"sort_tests": True, "skip_frac": 0.5, "p_est": 0.3}):
            ok &= compare(f"q10007_e23[:{rows}] B=3000 {flags}", sp, 3000, 4096, [0, 4096 * 7, 123456789], flags)
    sp = dict(camp)
    sp["residual"] = camp["residual"][:25]
    for flags in ({"sort_tests": True, "skip_frac": 0.5, "p_est": 0.055}, {"skip_frac": 0.8, "p_est": 0.055}):
        ok &= compare(f"campaign3[:25] B=50000 {flags}", sp, 50000, 2048, [0, 2048 * 5000 + 17], flags)
    sp["residual"] = camp["residual"][:300]
    ok &= compare("campaign3[:300] B=1e6 skip .97", sp, 1000000, 8192, [8192 * 11], {"sort_tests": True, "skip_frac": 0.97, "p_est": 0.055})
    if a.full:
        ok &= compare("campaign3 B=1e6 skip .92 sort", camp, 1000000, 32768, [32768 * 5],
                      {"sort_tests": True, "skip_frac": 0.92, "p_est": 0.055})

    print("command lines: log line and found file")
    with tempfile.TemporaryDirectory() as d:
        for name, spec_ in (("q10007_e23[:30]", dict(small, residual=small["residual"][:30], kmax=40000, name="t1")),
                            ("campaign3[:25]", dict(camp, residual=camp["residual"][:25], kmax=6144, name="t2"))):
            sf = os.path.join(d, "spec.json")
            json.dump(spec_, open(sf, "w"))
            for extra in (["--procs", "3", "--block", "2048", "--sieve-b", "3000", "--sort-tests", "--skip-frac", "0.8", "--p-est", "0.3"],
                          ["--procs", "2", "--block", "1024", "--sieve-b", "20000", "--skip-frac", "0.5"]):
                la, fa = cli(os.path.join(GB, "search.py"), sf, extra, os.path.join(d, "a.jsonl"))
                lb, fb = cli(os.path.join(HERE, "search_c.py"), sf, extra, os.path.join(d, "b.jsonl"))
                same = la == lb and fa == fb
                ok &= same
                print(f"  {name:<18s} {' '.join(extra[:4]):<28s} {'identical' if same else 'DIFFERENT'}   {lb[-1][:110] if lb else ''}")
                if not same:
                    print("   search.py:  ", la, "\n   search_c.py:", lb)
                for f in ("a.jsonl", "b.jsonl"):
                    if os.path.exists(os.path.join(d, f)):
                        os.remove(os.path.join(d, f))
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
