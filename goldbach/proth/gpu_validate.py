# Colab GPU validation for gpu_screen.py: exact residues vs gmpy2 at 120/3k/20k bits,
# an adversarial 2,000-limb carry chain, and the 2e6 spec (t=1306 prime, neighbours not).
# Expects gpu_screen.py and spec2m.json (desert.py build 2000000) in /content.
import json, os, random, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gmpy2"], check=True)
sys.path.insert(0, "/content")
sys.set_int_max_str_digits(0)
import gmpy2
import importlib, gpu_screen as gs
importlib.reload(gs)

rng = random.Random(20261121)


def check(n, mbits, B, label):
    ms = [gmpy2.mpz(rng.getrandbits(mbits) | (1 << (mbits - 1))) for _ in range(B)]
    bs = gs.BatchScreen(n, ms, gmpy2)
    t0 = time.time()
    try:
        res, err = bs.run(check_every=0)
    except RuntimeError as e:
        print(f"{label}: P ~{bs.P[0].bit_length()} bits, L={bs.L}, N={bs.N}: RUNTIME ERROR {e} (maxerr {bs.max_rounding_error():.2e})", flush=True)
        return False
    dt = time.time() - t0
    exp = [int(gmpy2.powmod(2, (p - 1) // 2, p)) for p in bs.P]
    bad = sum(1 for a, b in zip(res, exp) if a != b)
    print(f"{label}: P ~{bs.P[0].bit_length()} bits, L={bs.L}, N={bs.N}, B={B}: "
          f"{B - bad}/{B} residues exact, max rounding err {err:.2e}, {dt:.1f}s", flush=True)
    return bad == 0


ok = True
# adversarial carry: 2000 limbs of 0x7FFF with +1 at the bottom must ripple to the top
import numpy as np, cupy as cp
bsx = gs.BatchScreen(40, [gmpy2.mpz(3) << 2000], gmpy2)
row = np.full((1, 2001), float(gs.MASK)); row[0, 0] += 1.0; row[0, 2000] = 0.0
bsx.B = 1; bsx.rowflag = cp.zeros(1, dtype=cp.int32)
out = np.rint(cp.asnumpy(bsx._norm(cp.asarray(row), 2001, 2001))).astype(int)
good = (out[0, :2000] == 0).all() and out[0, 2000] == 1
print("adversarial 2000-limb carry chain:", "exact" if good else f"WRONG {out[0, :4].tolist()} ... {out[0, -3:].tolist()}", flush=True)
ok &= bool(good)
ok &= check(40, 80, 64, "tiny ")
ok &= check(1000, 2000, 32, "3k   ")
ok &= check(7000, 13000, 16, "20k  ")
spec = json.load(open("/content/spec2m.json"))
flags, err, bs = gs.screen(spec, [1305, 1306, 1307], gmpy2)
exp = [int(gmpy2.powmod(2, (p - 1) // 2, p)) for p in bs.P]
print("2M spec t=1305,1306,1307 ->", flags, "| gmpy2 says ==1:", [e == 1 for e in exp],
      f"| err {err:.2e}", flush=True)
ok &= flags == {1305: False, 1306: True, 1307: False}
print("ALL OK" if ok else "VALIDATION FAILED")
