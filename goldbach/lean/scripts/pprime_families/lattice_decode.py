"""Family 1: Chinese remaindering with errors / with lists by lattice reduction, on the miniature.

Instance: the 37 primes s = 29..199 (P = their product), for each s a list L_s of classes; unknown N' = N/2 < B = 5e8
(N even).  An N agrees on the set A of primes with N mod s in L_s; its agreement amplitude is prod_{s in A} s.

Decoder (Howgrave-Graham's form of Coppersmith's method, as in Boneh's and Guruswami-Sahai-Sudan's CRT decoders):
G(x) = monic polynomial of degree l = max |L_s| with G(N') = 0 mod s exactly when N' mod s is in the list (by CRT from
prod_{a in L_s} (x - a)); lattice spanned by x^j P^(a-i) G(x)^i (i < a, j < l) and x^j G(x)^a (j <= a'), evaluated at
xB.  Every N' < B whose amplitude exceeds  (sqrt(d) |v|)^(1/a)  is an integer root of the polynomial of the reduced
vector v, so each run comes with a certified threshold: all N' above it are returned.  Asymptotically the threshold is
P^sqrt(l ln B / ln P).

  python lattice_decode.py planted   decoder checked on planted N' just above its certified threshold
  python lattice_decode.py real      the miniature's own instance, lists of 1, 2, 3 classes, and the radius table
Work is reported as CPU seconds and in units of one member scored at depth 200 (110 ns)."""
import math, random, sys, time
from flint import fmpz, fmpz_mat, fmpz_poly

UNIT = 110e-9
B = 500_000_000

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

ROWS = [p for p in primes_upto(999) if p > 2]
DEEP = [p for p in primes_upto(199) if p >= 29]

def ranked_classes(s):
    w = [0] * s
    for q in ROWS: w[q % s] += 1
    return sorted(range(s), key=lambda a: (-w[a], a)), w

def half_class(a, s):                       # N = a mod s  <=>  N' = N/2 = a * 2^-1 mod s
    return a * pow(2, -1, s) % s

def crt_poly(lists, moduli):
    """monic G of degree l with G(x) = prod_{a in L_s}(x - a) mod s; shorter lists are padded with repeated roots"""
    P = math.prod(moduli); l = max(len(L) for L in lists); coeffs = [0] * (l + 1)
    for L, s in zip(lists, moduli):
        L = list(L) + [L[0]] * (l - len(L))
        g = [1]
        for a in L:                         # multiply by (x - a) mod s
            g = [((g[i - 1] if i > 0 else 0) - a * (g[i] if i < len(g) else 0)) % s for i in range(len(g) + 1)]
        e = (P // s) * pow(P // s, -1, s)
        for i in range(l + 1): coeffs[i] = (coeffs[i] + e * g[i]) % P
    coeffs[l] = 1
    return coeffs, P

def decode(lists, moduli, a, ap, bound=B):
    """returns (roots, ln threshold, d, seconds): every N' < bound with ln amplitude > ln threshold is among the roots"""
    t0 = time.process_time()
    G, P = crt_poly(lists, moduli); l = len(G) - 1; d = l * a + ap + 1
    Gp = fmpz_poly(G); X = fmpz_poly([0, 1]); polys = []
    Gi = fmpz_poly([1])
    for i in range(a):
        for j in range(l): polys.append(fmpz(P) ** (a - i) * Gi * X ** j)
        Gi = Gi * Gp
    for j in range(ap + 1): polys.append(Gi * X ** j)
    rows = []
    for p in polys:
        c = [int(x) for x in p.coeffs()] + [0] * d
        rows.append([c[k] * bound ** k for k in range(d)])
    M = fmpz_mat(rows).lll()
    roots = set(); thr = None
    for r in range(d):
        v = [int(M[r, k]) for k in range(d)]
        norm2 = sum(x * x for x in v)
        if norm2 == 0: continue
        ln_thr = (0.5 * math.log(d) + 0.5 * math.log(norm2)) / a
        if thr is None: thr = ln_thr
        if r >= 3: break                                  # the first vectors are enough; the certificate is for the first
        h = fmpz_poly([v[k] // bound ** k for k in range(d)])
        for fac, mult in h.factor()[1]:
            if fac.degree() == 1:
                c0, c1 = int(fac[0]), int(fac[1])
                if c1 != 0 and (-c0) % c1 == 0:
                    x = (-c0) // c1
                    if 0 <= x < bound: roots.add(x)
    return roots, thr, d, time.process_time() - t0

def amplitude(x, lists, moduli):
    return sum(math.log(s) for L, s in zip(lists, moduli) if x % s in L)

def agree_count(x, lists, moduli):
    return sum(1 for L, s in zip(lists, moduli) if x % s in L)

def real_lists(l):
    out = []
    for s in DEEP:
        order, _ = ranked_classes(s)
        out.append([half_class(a, s) for a in order[:l]])
    return out

def planted():
    rng = random.Random(2026); lnP = sum(math.log(s) for s in DEEP)
    print(f"# 37 primes 29..199, ln P = {lnP:.2f}, ln B = {math.log(B):.2f}; asymptotic radius sqrt(l ln B ln P) = "
          + ", ".join(f"l={l}: {math.sqrt(l * math.log(B) * lnP):.1f} nats" for l in (1, 2, 3)))
    print("lists | a | a' | lattice dimension | certified threshold (nats of agreeing primes) | planted amplitude | planted N' recovered | CPU s")
    for l, a, ap in ((1, 2, 2), (1, 4, 5), (1, 8, 10), (1, 12, 16), (1, 16, 22), (2, 3, 4), (2, 6, 8), (2, 9, 12), (3, 3, 4), (3, 5, 8), (3, 7, 12)):
        lists = real_lists(l)
        roots, thr, d, sec = decode(lists, DEEP, a, ap)
        # plant: N0 random; put its residue into the list (replacing the last class) for primes of total size just above the threshold
        ok = 0; trials = 5; amp_used = 0.0
        for _ in range(trials):
            n0 = rng.randrange(B); order = DEEP[:]; rng.shuffle(order); amp = 0.0; pl = [list(L) for L in lists]
            for s in order:
                if amp > thr + 0.5: break
                i = DEEP.index(s)
                if n0 % s not in pl[i]: pl[i][-1] = n0 % s
                amp += math.log(s)
            amp = amplitude(n0, pl, DEEP); amp_used = amp
            r2, thr2, _, _ = decode(pl, DEEP, a, ap)
            ok += (n0 in r2) and (amp > thr2)
        print(f"{l} | {a} | {ap} | {d} | {thr:.1f} | {amp_used:.1f} | {ok}/{trials} | {sec:.2f}", flush=True)

def real():
    lnP = sum(math.log(s) for s in DEEP)
    print(f"# the miniature's own lists; ln P = {lnP:.2f}, ln B = {math.log(B):.2f}")
    print("lists (best classes of every prime 29..199) | lattice dimension | certified threshold, nats | N' returned by the decoder | of which above the threshold | largest amplitude among the returned | CPU s | work in units")
    for l, a, ap in ((1, 16, 22), (2, 9, 12), (3, 7, 12)):
        lists = real_lists(l)
        roots, thr, d, sec = decode(lists, DEEP, a, ap)
        amps = sorted((amplitude(x, lists, DEEP) for x in roots), reverse=True)
        above = sum(1 for x in amps if x > thr)
        print(f"{l} | {d} | {thr:.1f} | {len(roots)} | {above} | {(f'{amps[0]:.1f}' if amps else '-')} | {sec:.2f} | {sec / UNIT:,.0f}", flush=True)
    # radius for fatter lists: the method needs l <= ln P / ln B even with every prime agreeing
    print(f"# largest list size for which the radius is below ln P (every prime agreeing): l <= ln P / ln B = {lnP / math.log(B):.2f}")
    print("# weighted radius of Guruswami-Sahai-Sudan, sqrt(ln B sum w^2 / ln s), for the weights that matter:")
    for name, wfun in (("one-class lists, weight 1", lambda s, w, a, rank: 1.0 if rank < 1 else 0.0),
                       ("lists of 2, weight 1", lambda s, w, a, rank: 1.0 if rank < 2 else 0.0),
                       ("lists of 3, weight 1", lambda s, w, a, rank: 1.0 if rank < 3 else 0.0),
                       ("lists of a third, weight 1", lambda s, w, a, rank: 1.0 if rank < s // 3 else 0.0),
                       ("weight = rows struck by the class", lambda s, w, a, rank: float(w[a])),
                       ("weight = rows struck minus the average of the prime", lambda s, w, a, rank: w[a] - sum(w) / s)):
        tot = 0.0; best = 0.0
        for s in DEEP:
            order, w = ranked_classes(s); rank = {a: i for i, a in enumerate(order)}
            ws = [wfun(s, w, a, rank[a]) for a in range(s)]
            tot += sum(x * x for x in ws) / math.log(s); best += max(ws)
        print(f"#   {name}: radius {math.sqrt(math.log(B) * tot):.1f}; agreement if N sat in the best class of every prime: {best:.1f}")

if __name__ == "__main__":
    {"planted": planted, "real": real}[sys.argv[1]]()
