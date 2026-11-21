# Known-answer check run on each new Colab GPU before it searches: sections 2-3 of
# gpu_validate_v3.py (exact residues vs gmpy2, the 2e6 and 1.2e6 known primes and neighbours).
# Colab validation of gpu_screen.mont_sq3 (v3, v2's arithmetic without the copies):
# 1. bit-for-bit: v3's state equals v2's after every one of S squarings (random f = 1/2
#    pattern) at the 5e6, 1e7 and 16M rung sizes;
# 2. exact residues 2^((P-1)/2) mod P vs gmpy2 at 120/3k/20k bits;
# 3. the 2e6 spec gives F/T/F at t = 1305..1307, and the eight known primes of the
#    1.2e6 increasing-cover progression pass while their 16 neighbours fail;
# 4. speed of v2 vs v3 per squaring (GPU shared with the running campaign).
# Expects gpu_screen.py, spec2m.json and spec12_inc.json in /content.
import json, random, sys, time
sys.path.insert(0, "/content")
sys.set_int_max_str_digits(0)
import importlib, gmpy2, numpy as np, cupy as cp
import gpu_screen as gs
importlib.reload(gs)
rng = random.Random(20261122)
ok = True

# ---- 2. exact residues ------------------------------------------------------------
gs.BatchScreen.use_v3 = True
def check(n, mbits, B, label):
    ms = [gmpy2.mpz(rng.getrandbits(mbits) | (1 << (mbits - 1))) for _ in range(B)]
    bs = gs.BatchScreen(n, ms, gmpy2)
    t0 = time.time(); res, err = bs.run(check_every=0); dt = time.time() - t0
    exp = [int(gmpy2.powmod(2, (p - 1) // 2, p)) for p in bs.P]
    bad = sum(1 for a, b in zip(res, exp) if a != b)
    print(f"v3 {label}: P ~{bs.P[0].bit_length()} bits B={B}: {B-bad}/{B} exact, err {err:.1e}, {dt:.1f}s", flush=True)
    return bad == 0
ok &= check(40, 80, 64, "tiny")
ok &= check(1000, 2000, 32, "3k")
ok &= check(7000, 13000, 16, "20k")

# ---- 3. known answers -------------------------------------------------------------
spec = json.load(open("/content/spec2m.json"))
flags, err, _ = gs.screen(spec, [1305, 1306, 1307], gmpy2)
print("v3 2M t=1305..1307:", flags, f"err {err:.1e}", flush=True)
ok &= flags == {1305: False, 1306: True, 1307: False}
spec = json.load(open("/content/spec12_inc.json"))
primes = [5568, 9736, 9970, 13340, 13563, 14787, 15048, 15135]
ts = sorted(set(primes + [t + 1 for t in primes] + [t - 1 for t in primes]))
flags, err, _ = gs.screen(spec, ts, gmpy2)
got = sorted(t for t in ts if flags[t])
print("v3 1.2M increasing: passes", got, "| expected", primes, f"| err {err:.1e}", flush=True)
ok &= got == primes
gs.BatchScreen.use_v3 = False
print("V3 ALL OK" if ok else "V3 VALIDATION FAILED", flush=True)

