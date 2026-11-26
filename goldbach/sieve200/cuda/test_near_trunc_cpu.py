#!/usr/bin/env python3
"""near_trunc.py (search_gpu5 --near-truncate 1): the row list cut at the near-miss threshold G, on the CPU with real numbers.

    python3 test_near_trunc_cpu.py

1. The helpers: truncate_spec keeps the whole list, is idempotent, full_spec restores it.
2. The pipeline on the cut list selects exactly what a selection by c_G (the alive rows below G) over the FULL list selects: sieve200's CPU Feeder on the truncated rows against numpy on the alive matrix of
   the full rows (same blocks, same keep rule, stable ties): the same members, each with its alive rows below G.
3. The near-misses are the same: for every kept member, the verdict of the truncated pipeline (base-2 Fermat tests of the rows below G; none probable prime -> settle_successes: the CPU finds the first
   probable prime among the rows at or above G, or the full list is a success) equals the ground truth of the full list (first probable-prime row of the member's alive rows, rows ascending):
   a member is a near-miss at q exactly when that first row is q >= G, and a design success exactly when there is none.  G is chosen low enough that plenty of members are near-misses.
"""
import json, math, os, sys, time
import numpy as np
import gmpy2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from sieve200 import Sieve200, Feeder
import near_trunc
import search


def fermat2(n):
    return gmpy2.powmod(2, n - 1, n) == 1


def main():
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec = spec[0] if isinstance(spec, list) else spec
    for f in ("residual", "cover"):
        if isinstance(spec.get(f), str):
            spec[f] = json.loads(spec[f])
    ok = True
    N0, M = int(spec["N0"]), int(spec["M"])
    U = [int(q) for q in spec["residual"]]
    cover = [int(r) for r, _ in spec["cover"]]
    G = 6000

    # 1. helpers
    s1 = near_trunc.truncate_spec(dict(spec), G)
    s2 = near_trunc.truncate_spec(dict(s1), G)
    good = (s1["residual"] == [q for q in U if q < G] and s1["residual_full"] == U and s2["residual"] == s1["residual"] and s2["residual_full"] == U
            and near_trunc.full_spec(s1)["residual"] == U and near_trunc.full_spec(spec) is spec and len(s1["residual"]) < len(U))
    print(f"  truncate_spec at {G}: {len(s1['residual'])} of {len(U)} rows, whole list kept, idempotent, full_spec restores it: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good

    # 2. the pipeline on the cut list == selection by c_G over the full list
    B, logK, L, f = 200_003, 15, 1 << 12, 0.9
    k0 = -(-10 ** 199 // M)
    ut = [q for q in U if q < G]
    nt = len(ut)
    sv_full = Sieve200(N0, M, U, B, logK=logK, exclude=cover)
    cnt_full, bits_full = sv_full.block(k0, counts=True)
    alive = sv_full.alive(bits_full)                                    # [nU, K] bool
    cG = alive[:nt].sum(axis=0).astype(np.int32)
    fd = Feeder(N0, M, ut, B=B, L=L, logK=logK, f=f, p_est=0.055, exclude=cover)
    blocks = fd.window(k0)
    nkeep = int(math.ceil(L * (1.0 - f)))
    members, lists = {}, {}
    same_sets, same_rows = True, True
    for bi, fb in enumerate(blocks):
        order = np.argsort(cG[bi * L:(bi + 1) * L], kind="stable")[:nkeep]
        want = (order + bi * L + k0).astype(np.uint64)
        got = np.asarray(fb.k, dtype=np.uint64)
        same_sets &= np.array_equal(np.sort(want), np.sort(got))
        for i, k in enumerate(fb.k.tolist()):
            rws = fb.rows[fb.offs[i]:fb.offs[i + 1]].astype(np.int64)
            ref = np.nonzero(alive[:, int(k) - k0])[0]
            ref_below = ref[ref < nt]
            same_rows &= np.array_equal(rws, ref_below)
            members[int(k)] = int(k) - k0
            lists[int(k)] = (rws, ref)                                   # rows below G (what the cut pipeline tests), all alive rows of the full list (ground truth)
    print(f"  Feeder on the {nt} rows below {G} vs numpy selection by c_G over the full {len(U)} rows (B {B:,}, {len(blocks)} blocks of {L}, keep {nkeep}): same members {same_sets}, "
          f"same alive rows below G {same_rows}: {'ok' if same_sets and same_rows else 'FAILED'}", flush=True)
    ok &= same_sets and same_rows

    # 3. the verdicts
    spec_t = near_trunc.truncate_spec(dict(spec, fast_verify=True), G)
    t0 = time.time()
    n_near = n_design = n_hit = 0
    bad = 0
    gpu_succ, truth = [], {}
    for k, (rows_t, rows_all) in lists.items():
        n = N0 + int(k) * M
        qf = None                                                         # ground truth: first PRP of the full alive list
        for r in rows_all:
            if fermat2(n - U[int(r)]):
                qf = U[int(r)]
                break
        truth[k] = qf
        hit_below = any(fermat2(n - U[int(r)]) for r in rows_t)         # the cut pipeline: a PRP among the rows below G -> not a near-miss
        if not hit_below:
            gpu_succ.append(k)
        if hit_below and not (qf is not None and qf < G):
            bad += 1
    near = []
    found = near_trunc.settle_successes(spec_t, gpu_succ, G, search.verify_success, near)
    found_k = {k for k, _ in found}
    near_d = dict(near)
    for k in gpu_succ:
        qf = truth[k]
        if qf is None:
            n_design += 1
            bad += not (k in found_k and k not in near_d)
        else:
            n_near += (qf >= G)
            bad += not (k not in found_k and near_d.get(k) == qf and qf >= G)
    for k, qf in truth.items():                                           # every member the cut pipeline did not call a near-miss has its first PRP below G
        if k not in set(gpu_succ):
            n_hit += 1
            bad += not (qf is not None and qf < G)
    good = bad == 0 and n_near > 0 and len(gpu_succ) == n_near + n_design
    print(f"  {len(lists)} kept members: {n_hit} with a probable prime below {G}, {len(gpu_succ)} with none (the GPU's 'successes'): {n_near} near-misses (first PRP q >= G found on the CPU, equal to the "
          f"full list's), {n_design} design successes; {bad} disagreements with the full-list ground truth in {time.time() - t0:.1f} s: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    # the design-success branch (never reached at this scale: every row composite): a stub verify_success decides, the rest follows
    calls = []
    fake_prp = {10: 777, 11: None, 12: 999}
    orig = near_trunc.first_prp_row
    near_trunc.first_prp_row = lambda spec, k, thr, reps=25: fake_prp[k]
    try:
        near2 = []
        found2 = near_trunc.settle_successes(spec_t, [12, 10, 11], G, lambda sp, k: (calls.append((k, len(sp["residual"]))) or ({"g": 170001} if k == 11 else None)), near2)
    finally:
        near_trunc.first_prp_row = orig
    good = (found2 == [(11, {"g": 170001})] and near2 == [(10, 777), (12, 999)] and calls == [(10, len(U)), (11, len(U)), (12, len(U))])
    print(f"  settle_successes with a stub: the full spec goes to verify_success (in k order), a verified success is a design record, a failed one with a first PRP row >= G is a near-miss: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    print("NEAR-TRUNC OK" if ok else "NEAR-TRUNC FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
