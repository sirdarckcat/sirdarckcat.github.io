"""Independent check of the closeness-frontier numbers of the research session, from N alone, and of the Pratt trees
it supplies (frontier_pratt.json, read as data).  Writes one record directory per number for scripts/gen_record.py
--lucas:  record.json (N, g, cover = the classes of N modulo the odd primes up to 43) and lucas.json (the internal
nodes of the Pratt tree as [n, root, prime factors of n - 1]).
  python -I check_frontier.py frontier_pratt.json OUTDIR"""
import json, math, os, sys

def primes_below(n):
    s = bytearray([1]) * n; s[0:2] = b"\0\0"
    for i in range(2, math.isqrt(n) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n) if s[i]]
SMALL = primes_below(100000)
def sprp(n, a):
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    x = pow(a, d, n)
    if x in (1, n - 1): return True
    for _ in range(r - 1):
        x = x * x % n
        if x == n - 1: return True
    return False
def probable_prime(n):
    if n < 2: return False
    for p in SMALL[:30]:
        if n % p == 0: return n == p
    return all(sprp(n, a) for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53))
def is_small_prime(n): return n < 100000 and n in SMALLSET
SMALLSET = set(SMALL)

def walk(node, out, depth=0):
    """checks a Pratt node; returns (nodes, max depth)"""
    n = int(node["n"])
    if "a" not in node:
        assert n < 1000 and n in SMALLSET, f"leaf {n} is not a prime below 1,000"
        return 1, depth
    a = int(node["a"]); qs = [int(f["n"]) for f in node["factors"]]
    assert pow(a, n - 1, n) == 1, f"{a}^({n}-1) != 1 mod {n}"
    m = n - 1
    for q in qs:
        assert m % q == 0 and pow(a, (n - 1) // q, n) != 1, f"node {n}: factor {q} fails"
        while m % q == 0: m //= q
    assert m == 1, f"node {n}: the listed factors do not exhaust n - 1 (left {m})"
    assert len(set(qs)) == len(qs)
    out.append([n, a, qs]); cnt, dmax = 1, depth
    for f in node["factors"]:
        c, d = walk(f, out, depth + 1); cnt += c; dmax = max(dmax, d)
    return cnt, dmax

data = json.load(open(sys.argv[1])); outdir = sys.argv[2]
for e in data:
    N = int(e["N"]); g = int(e["g"]); d = len(str(N))
    assert N % 2 == 0 and d == int(e["digits"]) and N - g == int(e["N_minus_g"])
    # the least prime p with N - p prime, from N alone
    first = next(p for p in SMALL if probable_prime(N - p))
    below = sum(1 for p in SMALL if p < g)
    fermat_pass = [p for p in SMALL if p < g and pow(2, N - p - 1, N - p) == 1]
    lucas = []; cnt, depth = walk(e["pratt"], lucas)
    assert int(e["pratt"]["n"]) == N - g
    cover = [[r, N % r] for r in SMALL if 3 <= r <= 43]
    struck = sum(1 for p in SMALL if p < g and any((N - p) % r == 0 for r, _ in cover))
    name = f"frontier_{d}digit_g{g}"; os.makedirs(f"{outdir}/{name}", exist_ok=True)
    json.dump({"N": str(N), "g": g, "cover": cover}, open(f"{outdir}/{name}/record.json", "w"))
    # deduplicate nodes (a prime can occur in several places of the tree)
    seen = {}; 
    for n, a, qs in lucas: seen.setdefault(n, [n, a, qs])
    json.dump(list(seen.values()), open(f"{outdir}/{name}/lucas.json", "w"))
    print(f"N = {N} ({d} digits, even): least prime p with N - p a probable prime = {first} (claimed g = {g}: {'agrees' if first == g else 'DISAGREES'}); "
          f"primes below g: {below}, struck by a modulus 3..43: {struck}, left: {below - struck}, of which passing the base-2 Fermat test: {len(fermat_pass)}; "
          f"Pratt tree of N - g: {cnt} nodes, depth {depth}, {len(seen)} distinct internal nodes, all checks pass -> {name}")
