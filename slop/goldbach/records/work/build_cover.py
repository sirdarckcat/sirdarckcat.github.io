#!/usr/bin/env python3
"""Build a partial 'Goldbach cover': choose prime moduli r with residues b_r
(meaning we will force N ≡ b_r (mod r)) so that as many primes p <= Q as
possible fall in some class p ≡ b_r (mod r)  (=> r | N - p, complement composite),
subject to sum(ln r) <= budget nats.

Outputs JSON: {"Q":..., "budget":..., "classes": [[r,b],...], "residual": [...]}
Optimization: greedy (lazy, gain/cost ratio) + coordinate descent + ruin&recreate.
"""
import argparse, json, math, sys, time
import numpy as np

def prime_sieve(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i*i::i] = False
    return np.nonzero(s)[0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Q", type=int, required=True, help="cover odd primes <= Q")
    ap.add_argument("--budget", type=float, required=True, help="nats of modulus")
    ap.add_argument("--pool-max", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--minutes", type=float, default=5.0)
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--init", type=str, default=None, help="warm-start cover json")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    targets = prime_sieve(a.Q)[1:].astype(np.int64)   # odd primes 3..Q
    nt = len(targets)
    pool = prime_sieve(a.pool_max)[1:].astype(np.int64)
    logs = {int(r): math.log(r) for r in pool}
    tm = {}                                            # cache: targets % r
    CACHE_LIM = 6000
    def tmod(r):
        v = tm.get(r)
        if v is None:
            v = (targets % r).astype(np.int32)
            if len(tm) < CACHE_LIM: tm[r] = v
        return v

    cover = np.zeros(nt, dtype=np.int16)               # how many chosen classes cover each target
    chosen = {}                                        # r -> b
    spent = 0.0

    def class_members(r, b):
        return np.nonzero(tmod(r) == b)[0]

    def add(r, b):
        nonlocal spent
        cover[class_members(r, b)] += 1
        chosen[r] = b; spent += logs[r]

    def remove(r):
        nonlocal spent
        b = chosen.pop(r)
        cover[class_members(r, b)] -= 1
        spent -= logs[r]

    def best_b(r):
        """(gain, b): residue class of r covering most currently-uncovered targets."""
        unc = tmod(r)[cover == 0]
        if len(unc) == 0: return 0, 1
        cnt = np.bincount(unc, minlength=r)
        b = int(cnt.argmax()); return int(cnt[b]), b

    if a.init:
        for r, b in json.load(open(a.init))["classes"]:
            add(int(r), int(b))

    # ---------------- lazy greedy fill ----------------
    import heapq
    grasp = 0.0
    def greedy_fill():
        nonlocal grasp
        heap = []
        for r in pool:
            r = int(r)
            if r in chosen or spent + logs[r] > a.budget + 1e-9: continue
            g, b = best_b(r)
            if g: heapq.heappush(heap, (-g / logs[r], g, r, b))
        while heap:
            negsc, g, r, b = heapq.heappop(heap)
            if r in chosen or spent + logs[r] > a.budget + 1e-9: continue
            g2, b2 = best_b(r)
            if g2 <= 0: continue
            thr = (heap[0][0] if heap else 0.0) * (1.0 - grasp * rng.random())
            if heap and -g2 / logs[r] > thr - 1e-12:          # stale/noisy => reinsert
                heapq.heappush(heap, (-g2 / logs[r], g2, r, b2)); continue
            add(r, b2)
        return int((cover == 0).sum())

    k = greedy_fill()
    t0 = time.time()
    print(f"[greedy] k={k} moduli={len(chosen)} spent={spent:.1f}/{a.budget} nats", flush=True)

    # ---------------- improvement loop (simulated annealing) ----------------
    best_state = (k, dict(chosen))
    k_cur = k
    it = 0
    T0, T1 = max(4.0, k / 80), 0.4
    while time.time() - t0 < a.minutes * 60:
        it += 1
        frac = min(1.0, (time.time() - t0) / (a.minutes * 60))
        T = T0 * (T1 / T0) ** frac
        state_before = dict(chosen)
        grasp = 0.10 + 0.15 * rng.random()
        # residue perturbation: kick a few moduli to a random top-5 class
        kick = rng.choice(list(chosen.keys()), size=min(4, len(chosen)), replace=False)
        for r in kick:
            r = int(r)
            remove(r)
            unc = tmod(r)[cover == 0]
            if len(unc):
                cnt = np.bincount(unc, minlength=r)
                top = np.argsort(cnt)[-5:]
                add(r, int(rng.choice(top)))
            else:
                add(r, 1)
        # coordinate descent: re-pick residue of each chosen modulus
        order = list(chosen.keys()); rng.shuffle(order)
        for r in order:
            remove(r)
            g, b = best_b(r)
            add(r, b)
        # drop poorly-performing moduli + random ruin, refill greedily
        excl = {}
        for r in list(chosen.keys()):
            mem = class_members(r, chosen[r])
            excl[r] = int((cover[mem] == 1).sum()) / logs[r]
        worst = sorted(excl, key=excl.get)[:max(2, len(chosen)//30)]
        nruin = max(2, int(len(chosen) * (0.03 + 0.12 * rng.random())))
        ruin = list(rng.choice(list(chosen.keys()), size=min(nruin, len(chosen)), replace=False))
        for r in set(worst + [int(x) for x in ruin]):
            remove(r)
        k_new = greedy_fill()
        if k_new <= k_cur or rng.random() < math.exp(-(k_new - k_cur) / T):
            k_cur = k_new
            if k_new < best_state[0]:
                best_state = (k_new, dict(chosen))
        else:  # reject: restore previous state
            for r in list(chosen.keys()): remove(r)
            for r, b in state_before.items(): add(r, b)
        if it % 5 == 0 or k_cur == best_state[0]:
            print(f"[improve] k={k_cur} best={best_state[0]} T={T:.2f} moduli={len(chosen)} spent={spent:.1f} t={time.time()-t0:.0f}s", flush=True)
        if it % 10 == 0:  # checkpoint best state
            bk, bch = best_state
            sp = sum(logs[r] for r in bch)
            cc = np.zeros(nt, dtype=np.int16)
            for r, b in bch.items(): cc[class_members(r, b)] += 1
            json.dump({"Q": a.Q, "budget": a.budget, "spent": sp,
                       "classes": sorted([[int(r), int(b)] for r, b in bch.items()]),
                       "residual": [int(p) for p in targets[cc == 0]], "k": bk, "n_targets": nt},
                      open(a.out + ".ckpt", "w"))

    k, ch = best_state
    for r in list(chosen.keys()): remove(r)
    for r, b in ch.items(): add(r, b)
    residual = targets[cover == 0]
    assert int((cover == 0).sum()) == k
    out = {"Q": a.Q, "budget": a.budget, "spent": spent,
           "classes": sorted([[int(r), int(b)] for r, b in ch.items()]),
           "residual": [int(p) for p in residual], "k": k, "n_targets": nt}
    json.dump(out, open(a.out, "w"))
    print(f"[done] k={k} moduli={len(ch)} spent={spent:.2f} nats "
          f"(~{spent/math.log(10):.1f} digits) -> {a.out}", flush=True)

if __name__ == "__main__":
    main()
