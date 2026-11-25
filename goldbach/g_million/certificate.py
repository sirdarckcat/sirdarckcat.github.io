# T5: a compositeness certificate for a hit, for the Lean session and for any independent check. For every odd prime q < Q there
# is one line "q w", with w the reason N - q is composite:
#   - w = a modulus r of the cover with N = q (mod r), so r | N - q (the smallest such r);
#   - otherwise w = the least prime factor s <= B of N - q (found here from N alone, not taken from the sieve);
#   - otherwise w = F: N - q has no prime factor <= B and fails the base-2 Fermat test, 2^(N-q-1) != 1 (mod N - q).
# (q = 2 is left out: N - 2 is even.) The rows marked F are compared with the sieve's survivor list for the member, when given.
#   python3 certificate.py hit.json cover.txt out.txt [Q] [B] [survivors.txt]
# CERT_NO_FERMAT=1 skips the Fermat tests (to check the factor search alone).
import sys, os, json, time
import numpy as np
import gmpy2
from gmpy2 import mpz, powmod
from multiprocessing import Pool

def odd_primes_upto(n):
    """Odd primes <= n (odd-only sieve: index i stands for 2i + 1)."""
    m = (n - 1) // 2
    s = np.ones(m + 1, bool); s[0] = False
    for i in range(1, (int(n ** 0.5) - 1) // 2 + 1):
        if s[i]:
            p = 2 * i + 1
            s[(p * p) // 2::p] = False
    return 2 * np.nonzero(s)[0].astype(np.int64) + 1

def residues(N, primes):
    """N mod p for every p in primes (uint64, p < 2^31), from the 32-bit limbs of N, most significant first."""
    nb = (N.bit_length() + 31) // 32 * 4
    limbs = np.frombuffer(int(N).to_bytes(nb, "big"), dtype=">u4").astype(np.uint64)
    r = np.zeros(len(primes), np.uint64); sh = np.uint64(32)
    for L in limbs:
        r = ((r << sh) | L) % primes
    return r

def fermat_fails(args):
    n, q = args
    m = n - q
    return q, powmod(2, m - 1, m) != 1

if __name__ == "__main__":
    hitf, coverf, outf = sys.argv[1], sys.argv[2], sys.argv[3]
    Q = int(sys.argv[4]) if len(sys.argv) > 4 else 1000003
    B = int(float(sys.argv[5])) if len(sys.argv) > 5 else 10 ** 9
    survf = sys.argv[6] if len(sys.argv) > 6 else None
    t0 = time.time()
    txt = open(hitf).read().strip()
    hit = json.loads(txt) if txt.startswith("{") else dict(N=txt)
    N = mpz(hit["N"]); assert N % 2 == 0
    cover = [tuple(map(int, w.split(":"))) for l in open(coverf) if not l.startswith("#") for w in l.split()]
    X = max(r for r, a in cover)
    rows = odd_primes_upto(Q - 1); rows = rows[rows < Q]
    # 1. the cover: r | N - q exactly when q = N (mod r); N must lie in the class a_r of every modulus
    bad_class = [(r, a) for r, a in cover if int(N % r) != a]
    assert not bad_class, f"N is not in the cover's class for {bad_class[:5]}"
    w = np.zeros(len(rows), np.int64)
    for r, a in sorted(cover):
        m = (rows % r == a) & (w == 0)
        w[m] = r
    n_cov = int((w > 0).sum())
    left = rows[w == 0]
    print(f"N: {len(str(N))} digits; {len(rows):,} odd primes q < {Q:,}; {n_cov:,} covered by the {len(cover)} moduli (up to {X}); "
          f"{len(left):,} left ({time.time() - t0:.0f} s)", flush=True)
    # 2. least prime factor s in (X, B] of N - q for the rows left (s | N - q exactly when q = N (mod s))
    idx = {int(q): i for i, q in enumerate(rows.tolist())}
    lpf = {}                                       # q -> least prime factor found
    left_mask = np.zeros(Q, bool); left_mask[left] = True
    P = odd_primes_upto(B); P = P[P > X]
    print(f"{len(P):,} primes in ({X}, {B:,}] ({time.time() - t0:.0f} s)", flush=True)
    seg = 1 << 22
    for lo in range(0, len(P), seg):
        ps = P[lo:lo + seg]
        r = residues(N, ps.astype(np.uint64)).astype(np.int64)
        small = ps <= Q
        for s, rr in zip(ps[small].tolist(), r[small].tolist()):       # s <= Q: q = rr, rr + s, ...
            for q in range(rr, Q, s):
                if left_mask[q] and q not in lpf: lpf[q] = s
        big = ~small                                                    # s > Q: q = rr only
        m = big & (r < Q)
        qs, ss = r[m], ps[m]
        if len(qs):
            ok = left_mask[qs]
            for q, s in zip(qs[ok].tolist(), ss[ok].tolist()):         # ps increasing, so the first s seen is the least
                if q not in lpf: lpf[q] = s
        if (lo // seg) % 3 == 0:
            print(f"  primes {lo:,}..{lo + len(ps):,} of {len(P):,}: {len(lpf):,} rows with a factor ({time.time() - t0:.0f} s)", flush=True)
    for q, s in lpf.items(): w[idx[q]] = s
    fermat_rows = [int(q) for q in left.tolist() if int(q) not in lpf]
    print(f"{len(lpf):,} rows left have a prime factor in ({X}, {B:,}]; {len(fermat_rows):,} have none ({time.time() - t0:.0f} s)", flush=True)
    # 3. Fermat for the rest
    not_shown = []
    if os.environ.get("CERT_NO_FERMAT") != "1":
        with Pool(4) as pool:
            for q, fails in pool.imap_unordered(fermat_fails, [(N, q) for q in fermat_rows], chunksize=4):
                if not fails: not_shown.append(q)
        print(f"Fermat: {len(fermat_rows) - len(not_shown):,} of {len(fermat_rows):,} fail base 2 (composite); {len(not_shown)} pass "
              f"({time.time() - t0:.0f} s)", flush=True)
    for q in fermat_rows: w[idx[q]] = -1
    # 4. the sieve's survivor list for this member, if given
    same = None
    if survf and "k" in hit:
        for l in open(survf):
            t = l.split()
            if int(t[0]) == int(hit["k"]):
                surv = sorted(map(int, t[2:])); same = surv == sorted(fermat_rows)
                print(f"sieve survivors for k = {hit['k']}: {len(surv)}; same set as the rows with no factor <= B: {same}", flush=True)
                break
    with open(outf, "w") as f:
        f.write(f"# N - q is composite for every odd prime q < {Q} (N - 2 is even). One line per row: 'q r' with r a modulus of the cover and\n"
                f"# N = q (mod r); 'q s' with s the least prime factor of N - q, in ({X}, {B}]; 'q F' when N - q has no prime factor <= {B}\n"
                f"# and 2^(N-q-1) != 1 (mod N - q). N has {len(str(N))} digits (N.txt). Rows: {len(rows)}; by a modulus: {n_cov}; by a factor: "
                f"{len(lpf)}; by Fermat: {len(fermat_rows)}.\n")
        for q, x in zip(rows.tolist(), w.tolist()):
            f.write(f"{q} {'F' if x == -1 else x}\n")
    json.dump(dict(digits=len(str(N)), Q=Q, B=B, rows=len(rows), by_modulus=n_cov, by_factor=len(lpf), by_fermat=len(fermat_rows),
                   fermat_tested=os.environ.get("CERT_NO_FERMAT") != "1", not_shown=not_shown, sieve_survivors_match=same,
                   seconds=round(time.time() - t0)), open(outf + ".json", "w"), indent=1)
    print(f"wrote {outf} ({time.time() - t0:.0f} s)")
