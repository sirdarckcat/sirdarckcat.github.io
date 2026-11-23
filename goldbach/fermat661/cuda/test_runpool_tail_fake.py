#!/usr/bin/env python3
"""search_gpu5.py's run_pool (taken from the patched driver, path in argv[1]) on numpy standing in for cupy and a fake Fermat tester whose verdict depends only on (row, k): the per-member results (rows
counted up to the first PRP, PRP flag, success flag, first-PRP row) must be IDENTICAL whatever the round sizes, with the tail rule off (the old D = min(dmax, target // active)) and on
(--tail-target / --dtail: more rows of each member per round when few members are left), and the tail rule must cut the number of rounds.

    python3 test_runpool_tail_fake.py /path/to/patched/search_gpu5.py
"""
import ast, sys, types
import numpy as np

src = open(sys.argv[1]).read()
tree = ast.parse(src)
fn = next(ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_pool")

cp = types.ModuleType("cupy")
cp.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
cp.bool_ = np.bool_


def scatter_min(a, idx, vals):
    np.minimum.at(a, idx, vals)


cupyx = types.SimpleNamespace(scatter_min=scatter_min)
rounds = []


class Tester:
    def test(self, rowsv, kvv):
        rounds.append(int(rowsv.size))
        h = (rowsv.astype(np.uint64) * np.uint64(2654435761) + kvv.astype(np.uint64) * np.uint64(40503)) % np.uint64(1000)
        return (h < 71).astype(np.uint8)                               # ~7.1% of the tests are PRPs


rng = np.random.default_rng(5)
ok = True
for n in (3000, 50_000, 300_000):
    cnt = rng.integers(0, 400, n).astype(np.int64)
    indptr = np.concatenate([[0], np.cumsum(cnt)])
    cols = np.sort(rng.integers(0, 1262, int(cnt.sum())).astype(np.int32))        # (row ids; ascending within a member is not needed by the fake)
    # make rows ascending per member as the driver requires
    cols = np.concatenate([np.sort(rng.choice(1262, c, replace=False)) if c else np.zeros(0, np.int64) for c in cnt]).astype(np.int32)
    kv = rng.integers(0, 1 << 32, n).astype(np.int64)
    res = {}
    for name, tail in (("old rule", 0), ("tail 196608 / 96", 196608), ("tail 65536 / 256", 65536)):
        args = types.SimpleNamespace(profile_pool=0, dmax=8, target=1 << 20, tail_target=tail, dtail=96 if tail == 196608 else 256, kernel=28)
        ns = dict(cp=cp, cupyx=cupyx, np=np, args=args, time=__import__("time"))
        exec(fn, ns)
        rounds.clear()
        out = ns["run_pool"](Tester(), cp.asarray(kv), cp.asarray(cnt), cp.asarray(cols))
        res[name] = (out, len(rounds), int(sum(rounds)))
    ref = res["old rule"][0]
    for name, (out, nr, tot) in res.items():
        same = all(np.array_equal(np.asarray(out[k]), np.asarray(ref[k])) for k in range(4))
        good = same and (name == "old rule" or nr < res["old rule"][1] or n < 50_000)
        print(f"  {n:7d} members, {name:18s}: {nr:3d} rounds, {tot:9d} tests computed; counted tests identical to the old rule: {same}: {'ok' if good else 'FAILED'}")
        ok &= good
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
