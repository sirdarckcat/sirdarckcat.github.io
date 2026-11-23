#!/usr/bin/env python3
"""The persistent pool kernel (fermat28_persist, gpu_fermat28.persist_source()) compiled for the CPU with real threads, against sequential Python pow on the same members: for every member
the result must be what the round-based run_pool computes (rows tested in ascending order until the first base-2 PRP): tests counted, PRP flag, success flag, first-PRP row.  Members the kernel
leaves to the caller (state 0: the queue was empty) carry the rows already tested, all composite.  Then gpu_fermat28.persist_pool() (the host side: launch, gather the unfinished members' remaining
rows, round-based finish, merge) is run on numpy standing in for cupy and must give the same arrays as the reference for the whole pool.

    python3 test_fermat28_persist.py [--members 120] [--lanes 24] [--rows 400]
"""
import argparse, ctypes, json, os, random, subprocess, sys, tempfile, types
import numpy as np
import gmpy2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sieve200", "cuda"))


def build(step):
    sys.modules.setdefault("cupy", types.ModuleType("cupy"))
    import gpu_fermat28 as g
    tag = os.path.splitext(step)[0].replace("fermat28_", "")
    src = os.path.join(tempfile.gettempdir(), f"_persist_src_{tag}.cuh")
    open(src, "w").write(g.persist_source(step))
    out = os.path.join(HERE, f"libfermat28_persist_cpu_{tag}.so")
    deps = [os.path.join(HERE, f) for f in ("fermat28_persist_cpu.cpp", step, "fermat28_kernel.cuh", "fermat28_persist_kernel.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in deps):
        subprocess.check_call(["g++", "-O2", "-std=c++17", "-pthread", f'-DPERSIST_SRC="{src}"', "-Wno-unused", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, deps[0]])
    return out


def to_limbs(x, limbs=21):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--members", type=int, default=120)
    ap.add_argument("--lanes", type=int, default=24)
    ap.add_argument("--rows", type=int, default=400, help="candidate rows a member (after trial division: ~5% of them are prime)")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    step = os.environ.get("FM28_STEP", "fermat28_step_s1r.cuh")
    lib = ctypes.CDLL(build(step))
    vp = ctypes.c_void_p
    lib.run_persist_cpu.argtypes = [vp] * 11 + [ctypes.c_int]
    lib.run_persist_cpu.argtypes = [vp, vp, vp, vp, vp, vp, ctypes.c_int, vp, vp, vp, vp, ctypes.c_int]
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    N0, M = gmpy2.mpz(int(spec["N0"])), gmpy2.mpz(int(spec["M"]))
    U = sorted(int(q) for q in spec["residual"])
    rng = random.Random(a.seed)
    # trial division by the primes up to 2e5 makes ~4-5% of the surviving rows prime (members need ~20 tests)
    small = [int(p) for p in gmpy2.mpz(1) and __import__("sympy").primerange(3, 200000)]
    prods, cur = [], gmpy2.mpz(1)
    for p in small:
        cur *= p
        if cur.bit_length() > 4000:
            prods.append((cur, ) ); cur = gmpy2.mpz(1)
    prods.append((cur,))
    ps = [int(p) for p in small]
    def alive(n):
        for (P,) in prods:
            if gmpy2.gcd(n, P) != 1:
                return False
        return True
    CQ = np.stack([to_limbs(N0 - q) for q in U])
    Mv = to_limbs(M)
    ks, rows_of = [], []
    cands = list(range(len(U)))
    for mi in range(a.members):
        k = rng.randrange(1 << 30, 1 << 32)
        rows = []
        for r in cands:
            if alive(N0 - U[r] + k * M):
                rows.append(r)
            if len(rows) >= a.rows:
                break
        ks.append(k); rows_of.append(rows)
    cnt = np.array([len(r) for r in rows_of], dtype=np.int32)
    indptr = np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64)
    cols = np.concatenate([np.array(r, dtype=np.int32) for r in rows_of])
    kv = np.array(ks, dtype=np.uint32)
    n = a.members
    print(f"{n} members, {int(cnt.sum())} rows ({cnt.mean():.0f} a member after trial division), {a.lanes} lanes", flush=True)
    # reference: the first PRP in ascending row order, per member
    ref = []
    for mi in range(n):
        t, prp, frow = 0, False, -1
        for r in rows_of[mi]:
            t += 1
            nn = N0 - U[r] + ks[mi] * M
            if pow(2, nn - 1, nn) == 1:
                prp, frow = True, r
                break
        ref.append((t, prp, (not prp), frow))
    print(f"reference: {sum(r[1] for r in ref)} members have a PRP, tests counted {sum(r[0] for r in ref)}, mean {sum(r[0] for r in ref) / n:.1f}", flush=True)
    # 1. the kernel itself
    ok = True
    for lanes in (1, 3, a.lanes):
        counter = np.zeros(1, dtype=np.int32)
        tests = np.zeros(n, dtype=np.int32); state = np.full(n, 9, dtype=np.uint8); frow = np.full(n, -7, dtype=np.int32)
        P = lambda x: x.ctypes.data
        lib.run_persist_cpu(P(CQ), P(Mv), P(kv), P(cnt), P(indptr), P(cols), n, P(counter), P(tests), P(state), P(frow), lanes)
        bad = 0
        left = int((state == 0).sum())
        for mi in range(n):
            t, prp, succ, fr = ref[mi]
            if state[mi] == 1:
                bad += not (prp and tests[mi] == t and frow[mi] == fr)
            elif state[mi] == 2:
                bad += not (succ and tests[mi] == t == cnt[mi])
            elif state[mi] == 0:                                   # left to the caller: rows [0, tests) all composite, so the first PRP (if any) comes later
                bad += not (0 < tests[mi] < cnt[mi] and (not prp or t > tests[mi]))
            else:
                bad += 1
        good = bad == 0 and int(counter[0]) >= n
        print(f"  {lanes:3d} lanes: {int((state == 1).sum())} PRP, {int((state == 2).sum())} successes, {left} left to the caller, wrong {bad}, queue counter {int(counter[0])}: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
    # 2. the host side with numpy standing in for cupy
    import test_gpu_sieve_cpu as TG
    cp = TG.install_fake_cupy()
    cp.cuda.Device = lambda: types.SimpleNamespace(attributes={"MultiProcessorCount": 2, "MaxRegistersPerMultiprocessor": 65536, "MaxThreadsPerMultiProcessor": 1536}, synchronize=lambda: None, id=0)
    sys.modules.pop("gpu_fermat28", None)
    import gpu_fermat28 as g

    class Tester:
        pass
    tester = Tester()
    tester.cq, tester.M = CQ, Mv
    calls = []
    def kp(grid, block, args):
        CQ_, Mv_, kv_, cnt_, indptr_, cols_, nm, counter_, tests_, state_, frow_ = args
        calls.append((grid, block))
        P = lambda x: x.ctypes.data
        lib.run_persist_cpu(P(CQ_), P(Mv_), P(kv_), P(cnt_), P(indptr_), P(cols_), int(nm), P(counter_), P(tests_), P(state_), P(frow_), 16)
    tester.kp = kp
    tester.kp_regs = 96
    def run_rest(tester_, kv_, cnt_, cols_, target=None):
        """the round-based path stands in: a sequential reference over the members it is given (their remaining rows)"""
        t_out = np.zeros(len(kv_), np.int64); p_out = np.zeros(len(kv_), bool); s_out = np.zeros(len(kv_), bool); f_out = np.full(len(kv_), -1, np.int64)
        ip = np.concatenate([[0], np.cumsum(cnt_)])
        g_tests = 0
        for i in range(len(kv_)):
            rr = cols_[ip[i]:ip[i + 1]]
            t = 0; hit = False
            for r in rr:
                t += 1; g_tests += 1
                nn = N0 - U[int(r)] + int(kv_[i]) * M
                if pow(2, nn - 1, nn) == 1:
                    hit = True; f_out[i] = int(r); break
            t_out[i] = t; p_out[i] = hit; s_out[i] = not hit
        return t_out, p_out, s_out, f_out, g_tests, 1
    out = g.persist_pool(tester, cp.asarray(kv), cp.asarray(cnt.astype(np.int64)), cp.asarray(cols), run_rest, cta_sm=None)
    tm, pm, sm, fm, gt, nl = out
    bad = 0
    for mi in range(n):
        t, prp, succ, fr = ref[mi]
        bad += not (int(tm[mi]) == t and bool(pm[mi]) == prp and bool(sm[mi]) == succ and int(fm[mi]) == fr)
    good = bad == 0 and gt >= int(sum(r[0] for r in ref)) and gt <= int(cnt.sum())
    print(f"  persist_pool (kernel + remaining rows by the round-based path + merge): {n} members, wrong {bad}, tests computed {gt} (counted {sum(r[0] for r in ref)}), launch grid {calls[0][0]} x {calls[0][1]}: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    # 3. edge cases: members with no row (a success), with one row, a pool smaller than the grid, and an n outside the kernel's range (the caller must get a RuntimeError)
    small = [mi for mi in range(n) if cnt[mi] >= 2][:6]
    kv2 = np.array([ks[mi] for mi in small] + [ks[small[0]], ks[small[1]]], dtype=np.int64)
    rows2 = [rows_of[mi][:1] for mi in small[:3]] + [rows_of[mi][:40] for mi in small[3:]] + [[], rows_of[small[1]][:1]]
    cnt2 = np.array([len(r) for r in rows2], dtype=np.int64)
    cols2 = np.concatenate([np.array(r, dtype=np.int32) for r in rows2 if r])
    out2 = g.persist_pool(tester, cp.asarray(kv2), cp.asarray(cnt2), cp.asarray(cols2), run_rest)
    bad = 0
    for i, rr in enumerate(rows2):
        t, hit, fr = 0, False, -1
        for r in rr:
            t += 1
            nn = N0 - U[r] + int(kv2[i]) * M
            if pow(2, nn - 1, nn) == 1:
                hit, fr = True, r
                break
        bad += not (int(out2[0][i]) == t and bool(out2[1][i]) == hit and bool(out2[2][i]) == (not hit) and int(out2[3][i]) == fr)
    print(f"  edge cases (no row, one row, {len(rows2)} members for 12 lanes): wrong {bad}: {'ok' if bad == 0 else 'FAILED'}", flush=True)
    ok &= bad == 0
    CQ_bad = np.concatenate([CQ, to_limbs((1 << 600) + 1)[None, :]])            # a 601-bit n: the kernel returns 2, state 3
    tester.cq = CQ_bad
    try:
        g.persist_pool(tester, cp.asarray(np.array([5], dtype=np.int64)), cp.asarray(np.array([1], dtype=np.int64)), cp.asarray(np.array([len(CQ)], dtype=np.int32)), run_rest)
        raised = False
    except RuntimeError as e:
        raised = "outside its range" in str(e)
    print(f"  a number outside 2^642 .. 2^668 raises: {'ok' if raised else 'FAILED'}", flush=True)
    ok &= raised
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
