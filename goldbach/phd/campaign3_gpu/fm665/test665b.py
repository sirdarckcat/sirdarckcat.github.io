"""fm13 on 665-bit numbers, the upstream test's residue rule (y < 4n and y = 2^(1-n) mod n) and verdicts against Python pow;
then the member path (fm13.Members.first_pass, as search_c.py calls it) on the local share's spec v154 at k ~ 4.9e9 against a
plain gmpy2 loop; then where fm13 actually starts to fail (666-704 bits).  python3 -I test665b.py FERMAT661_DIR SPECS_JSON"""
import ctypes, hashlib, json, os, random, sys
import numpy as np
import gmpy2
F, SPECS = sys.argv[1], sys.argv[2]
sys.path.insert(0, F)
import fm13
tag = hashlib.sha1(("".join(l for l in open("/proc/cpuinfo") if l.startswith("model name"))).encode()).hexdigest()[:8]
so = os.path.join(F, f"libfm13-{tag}.so")
lib = ctypes.CDLL(so)
lib.fm13_test.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
NW = 11
tot = {"n": 0, "bad_y": 0, "bad_v": 0}
def check(label, ns, quiet=False):
    nw = np.concatenate([np.frombuffer(int(x).to_bytes(8 * NW, "little"), dtype=np.uint64) for x in ns]).copy()
    v = np.zeros(len(ns), dtype=np.uint8); y = np.zeros(len(ns) * NW, dtype=np.uint64)
    lib.fm13_test(len(ns), nw.ctypes.data, v.ctypes.data, y.ctypes.data)
    bad_y = bad_v = fc = fp = 0
    for i, n in enumerate(ns):
        yy = int.from_bytes(y[i * NW:(i + 1) * NW].tobytes(), "little")
        if yy >= 4 * n or yy % n != pow(2, -(n - 1), n):
            bad_y += 1
        t = pow(2, n - 1, n) == 1
        if bool(v[i]) != t:
            bad_v += 1; fc += t; fp += (not t)
    if not quiet:
        print(f"  {label:<58s} {len(ns):6d} numbers, bits {min(n.bit_length() for n in ns)}-{max(n.bit_length() for n in ns)}, "
              f"passes {int(v.sum()):5d}, wrong residues {bad_y}, wrong verdicts {bad_v} (false-composite {fc}, false-pass {fp})", flush=True)
    tot["n"] += len(ns); tot["bad_y"] += bad_y; tot["bad_v"] += bad_v
    return bad_y, bad_v
rng = random.Random(6650)
B664, TEN200 = 1 << 664, 10 ** 200
print("lib:", so)
print("[1] fm13_test on 665-bit numbers n in [2^664, 10^200)")
check("random odd", [rng.randrange(B664, TEN200) | 1 for _ in range(20000)])
check("random odd, top 1% of the range (n > 0.99e200)", [rng.randrange(99 * 10 ** 198, TEN200) | 1 for _ in range(5000)])
check("10^200 - j, j odd < 2000", [TEN200 - j for j in range(1, 2000, 2)])
check("2^664 + j, j odd < 2000", [B664 + j for j in range(1, 2000, 2)])
check("primes, uniform", [int(gmpy2.next_prime(rng.randrange(B664, TEN200 - 10 ** 160))) for _ in range(1500)])
check("primes just below 10^200", [int(gmpy2.prev_prime(TEN200 - rng.randrange(0, 10 ** 120))) for _ in range(300)])
ps = []
while len(ps) < 30:                                   # base-2 pseudoprimes p (k(p-1)+1) of 665 bits
    p = int(gmpy2.next_prime(rng.getrandbits(331) | (1 << 330)))
    for k in range(2, 4000, 2):
        q = k * (p - 1) + 1; n = p * q
        if n.bit_length() == 665 and n < TEN200 and gmpy2.is_prime(q) and pow(2, n - 1, n) == 1:
            ps.append(n); break
        if n >= TEN200: break
check("base-2 pseudoprimes p (k(p-1)+1), 665 bits", ps)
N = 95347106818046249718570776328527805394387907539756369117325081343361548773031798520383947495686099037769506167416423881905531645343709972339865033333397602306957446186830655985687114607924513408740178
check("the record N - p, p < 2000 prime, and N - 160357", [N - p for p in range(3, 2000) if gmpy2.is_prime(p)] + [N - 160357])
print("[2] fm13.Members.first_pass (search_c.py's call) on spec v154 against a plain gmpy2 loop")
s = [x for x in json.load(open(SPECS)) if x["name"].startswith("q150000_g8ffe1_v154")][0]
N0, M, U = int(s["N0"]), int(s["M"]), [int(q) for q in s["residual"]]
fm = fm13.Members(N0, M, U)
for trial, (nm, maxrows, klo) in enumerate(((300, 60, 4294967296), (300, 60, 4910481408), (200, 400, 5390000000), (2000, 8, 4162978815))):
    kv = [klo + rng.randrange(0, 1 << 24) for _ in range(nm)]
    rows, offs = [], [0]
    for _ in range(nm):
        r = sorted(rng.sample(range(len(U)), rng.randint(1, maxrows)))
        rows += r; offs.append(len(rows))
    got = fm.first_pass(np.array(kv, dtype=np.uint64), np.array(rows, dtype=np.uint16), np.array(offs, dtype=np.int64))
    bad = 0; withpass = 0; nb = set()
    for i, k in enumerate(kv):
        exp = -1
        for pos, r in enumerate(rows[offs[i]:offs[i + 1]]):
            n = N0 + k * M - U[r]
            nb.add(n.bit_length())
            if gmpy2.powmod(2, n - 1, n) == 1:
                exp = pos; break
        bad += exp != int(got[i]); withpass += exp >= 0
    print(f"  members trial {trial}: {nm} members at k >= {klo}, up to {maxrows} rows, bits {sorted(nb)}, {withpass} with a pass, wrong {bad}", flush=True)
    tot["bad_v"] += bad
print("[3] where fm13 starts to fail: 400 random odd and 60 primes at each size")
for bits in (666, 667, 668, 670, 672, 673, 674, 675, 676):
    by, bv = check(f"{bits} bits", [rng.getrandbits(bits) | (1 << (bits - 1)) | 1 for _ in range(400)] +
                   [int(gmpy2.next_prime(rng.getrandbits(bits - 1) | (1 << (bits - 1)))) for _ in range(60)])
print("TOTAL 665-bit + members: see [1] [2]; all sizes:", tot)
