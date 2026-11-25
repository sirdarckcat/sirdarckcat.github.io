"""Runs the three combinatorial families (families.c) on the miniature and scores every configuration against the truth.
One JSON line per configuration in results.jsonl.

Work is counted in units of one member scored at depth 200:
  work = (operations of the generation) / OPS_PER_UNIT  +  members among the candidates (each scored at depth 200)
with OPS_PER_UNIT = 90 (45 reductions and 45 three-word ORs; unit.c measures 110 ns), and one operation = one modular
reduction or multiplication, one comparison of a sort or search, one table probe or one candidate written.
The CPU time of the generation is recorded as well (cpu_units = seconds / 110 ns)."""
import json, math, os, resource, subprocess, sys
import numpy as np
import pp
from refcurve import cover_order, gains

OPS_PER_UNIT = 90.0; UNIT_SECONDS = 110e-9
DEEP = [29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157,
        163, 167, 173, 179, 181, 191, 193, 197, 199]
K1 = np.asarray(pp.K1); K2 = np.asarray(pp.K2); SU = np.asarray(pp.SUCC)
ORDER = cover_order()

def lsize(spec, s): return s // int(spec[1:]) if spec[0] == "f" else int(spec)

def run(args, out):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    p = subprocess.run(["./families"] + [str(a) for a in args[:1]] + [out] + [str(a) for a in args[1:]], capture_output=True, text=True, check=True)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    line = p.stdout.strip().splitlines()[-1]
    kv = dict(x.split("=", 1) for x in line.split() if "=" in x)
    ops = sum(int(kv[k]) for k in ("ops_arith", "ops_cmp", "outputs"))
    return {"line": line, "ops": ops, "outputs": int(kv["outputs"]), "memory": int(kv["memory"]),
            "cpu": (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)}

def capture(idx):
    kk = K2[idx]
    return {"successes": int(SU[idx].sum()), "le9": int((kk <= 9).sum()), "le10": int((kk <= 10).sum()), "le12": int((kk <= 12).sum())}

def score(cand, gen):
    idx, notmem = pp.index_of(cand); idx = np.sort(idx)
    k = K2[idx]; s = SU[idx]
    ex = pp.examined(k, s); exd = pp.examined(K1[idx], s)
    work = gen["ops"] / OPS_PER_UNIT + len(idx)
    Wr = int(round(min(max(work, 1), len(K1))))
    ridx = np.sort(np.asarray(ORDER[:Wr])); rex = pp.examined(K2[ridx], SU[ridx])
    frac = len(idx) / len(K1)
    return {"candidates": int(len(np.unique(cand))), "members": int(len(idx)), "not_members": int(notmem), "gen_ops": gen["ops"], "gen_cpu": gen["cpu"],
            "memory": gen["memory"], "work": work, "work_time_units": gen["cpu"] / UNIT_SECONDS + len(idx),
            **capture(idx), "examined": ex, "gain": gains(ex), "examined_cover_order": exd, "gain_cover_order": gains(exd),
            "random_expect": {"successes": 256 * frac, "le9": 401 * frac, "le10": 1965 * frac, "le12": 33598 * frac},
            "r2": {"W": Wr, **capture(ridx), "examined": rex, "gain": gains(rex)}}

def emit(fam, name, res, extra=None):
    rec = {"family": fam, "config": name, **res}
    if extra: rec.update(extra)
    with open("results.jsonl", "a") as f: f.write(json.dumps(rec) + "\n")
    g = res["gain"]; r = res["r2"]
    def c(d): return " ".join((f"{d[t]:+.2f}" if math.isfinite(d[t]) else "    -") for t in pp.TARGETS)
    print(f"{fam:7s} {name:44s} work {res['work']:>12,.0f} mem {res['memory']:>10,d} members {res['members']:>10,d} succ {res['successes']:>3d} (cover-first prefix of equal work {r['successes']:>3d}) "
          f"le10 {res['le10']:>5d} ({r['le10']:>5d}) gain {c(g)} | prefix {c(r['gain'])} | unscored {c(res['gain_cover_order'])}", flush=True)

def product_entropy(spec, T): return sum(math.log(lsize(spec, s)) for s in T)

DONE = set(); NAMES = set()
def main(which):
    if os.path.exists("results.jsonl"):
        for line in open("results.jsonl"):
            r = json.loads(line); NAMES.add((r["family"], r["config"]))
            if r["family"] == "mitm": DONE.add((r["spec"], r["t"]))
    out = f"out_run_{os.getpid()}.u32"
    if "mitm" in which:
        for spec, ts in (("1", (1, 2, 3)), ("2", (1, 2, 3, 4)), ("3", (1, 2, 3, 4, 5)), ("f3", (1, 2, 3, 4, 6, 8, 10)), ("f2", (1, 2, 4, 6, 8, 10))):
            for t in ts:
                T = DEEP[:t]
                if 5e8 * math.prod(lsize(spec, s) / s for s in T) > 2e7: continue      # more than 4% of all N: not a selection
                if (spec, t) in DONE: continue
                gen = run(["mitm", spec] + T, out); cand = np.fromfile(out, dtype=np.uint32)
                emit("mitm", f"lists {spec}, primes {T[0]}..{T[-1]} ({t})", score(cand, gen), {"spec": spec, "t": t, "list_entropy": product_entropy(spec, T)})
    if "ktree" in which:
        for spec, t, windows in (("f3", 6, 0), ("f3", 8, 0), ("f3", 10, 0), ("f2", 8, 0), ("f2", 10, 0), ("f2", 12, 0), ("f3", 12, 0),
                                 ("f3", 10, 1), ("f2", 12, 1), ("f3", 12, 1), ("f2", 14, 64), ("f3", 14, 64)):
            T = DEEP[:t]
            gen = run(["ktree", spec, windows] + T, out); cand = np.fromfile(out, dtype=np.uint32)
            emit("ktree", f"lists {spec}, primes {T[0]}..{T[-1]} ({t}), windows {windows or 'all'}", score(cand, gen),
                 {"spec": spec, "t": t, "windows": windows, "list_entropy": product_entropy(spec, T), "line": gen["line"]})
    if "prefix" in which:
        for c in (28, 29, 30, 31, 32, 33, 34, 35):
            R = os.path.getsize(f"data/prefix_{c}.u32") // 4
            for spec in ("1", "2", "3", "f3", "f2"):
                for t in (1, 2, 3, 4, 5):
                    T = DEEP[:t]
                    expect = R * 4.33 * math.prod(lsize(spec, s) / s for s in T)
                    if expect < 3000 or expect > 1.2e7 or math.prod(lsize(spec, s) for s in T) > 3e7: continue
                    gen = run(["prefix", spec, f"data/prefix_{c}.u32"] + T, out); cand = np.fromfile(out, dtype=np.uint32)
                    emit("prefix", f"rows at 23 <= {c}, lists {spec}, primes {T[0]}..{T[-1]} ({t})", score(cand, gen), {"spec": spec, "t": t, "c": c})
    if "bucket" in which:
        for spec, t, tables, pool in (("1", 2, 8, 8), ("1", 2, 28, 8), ("1", 3, 32, 10), ("2", 3, 32, 10), ("3", 3, 32, 10), ("3", 4, 64, 12),
                                      ("f3", 4, 8, 12), ("f3", 6, 8, 16), ("f3", 6, 32, 16), ("f3", 8, 64, 20), ("f3", 8, 256, 20), ("f2", 8, 16, 20),
                                      ("f3", 10, 32, 24)):
            if ("bucket", f"lists {spec}, {tables} tables of {t} primes from the first {pool}") in NAMES: continue
            gen = run(["bucket", spec, t, tables, 12345, pool], out); cand = np.fromfile(out, dtype=np.uint32)
            emit("bucket", f"lists {spec}, {tables} tables of {t} primes from the first {pool}", score(cand, gen), {"spec": spec, "t": t, "tables": tables, "pool": pool})
        # the same on the best covers: every table is a run of the sorted-list variant on the prefix
        rng = np.random.default_rng(99)
        for c, spec, t, tables, pool in ((31, "3", 2, 8, 8), (33, "3", 2, 16, 8), (33, "f3", 3, 16, 10), (35, "f3", 4, 16, 12), (33, "2", 2, 28, 8), (35, "f3", 4, 64, 12)):
            parts = []; ops = cpu = 0; mem = 0
            for _ in range(tables):
                T = sorted(int(x) for x in rng.choice(DEEP[:pool], size=t, replace=False))
                gen = run(["prefix", spec, f"data/prefix_{c}.u32"] + T, out); parts.append(np.fromfile(out, dtype=np.uint32))
                ops += gen["ops"]; cpu += gen["cpu"]; mem = max(mem, gen["memory"])
            cand = np.unique(np.concatenate(parts))
            emit("bucket", f"rows at 23 <= {c}, lists {spec}, {tables} tables of {t} primes from the first {pool}",
                 score(cand, {"ops": ops, "cpu": cpu, "memory": mem}), {"spec": spec, "t": t, "tables": tables, "pool": pool, "c": c})

if __name__ == "__main__":
    main(sys.argv[1:] or ["mitm", "ktree", "prefix", "bucket"])
