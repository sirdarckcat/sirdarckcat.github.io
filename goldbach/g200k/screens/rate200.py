"""CPU pipeline at 200 digits, one core: sieve200 to B, the emptiest `keep` of each 32,768-block, fm13 until the first PRP.
   python3 rate200.py cover.txt Q B logK keep [windows]"""
import sys, os, time, math, ctypes
GB = "/home/user/sirdarckcat.github.io/goldbach"
for p in ("sieve200", "fermat661", "fermatw", ""):
    sys.path.insert(0, os.path.join(GB, p))
import numpy as np
from sieve200 import Sieve200
from sympy import primerange
import fm13
src, Q, B, logK, keepf = sys.argv[1], int(sys.argv[2]), int(float(sys.argv[3])), int(sys.argv[4]), float(sys.argv[5])
nwin = int(sys.argv[6]) if len(sys.argv) > 6 else 1
t = open(src).readline().split()
cov = [tuple(map(int, x.split(":"))) for x in t[2:]]
P = np.array(list(primerange(3, Q)), dtype=np.int64)
alive = np.ones(len(P), bool)
for r, a in cov: alive &= (P % r) != a
U = P[alive].tolist()
M, N0 = 2, 0
for r, a in cov:
    tt = ((a - N0) * pow(M, -1, r)) % r; N0 += M * tt; M *= r
kmax = (10 ** 200 - N0) // M                      # N < 10^200
print(f"cover: {len(cov)} moduli, {len(U)} rows at Q={Q}; M has {len(str(M))} digits; k < {kmax:.3e} below 10^200; "
      f"N bits {(N0 + kmax * M).bit_length()}", flush=True)
t0 = time.time(); sv = Sieve200(N0, M, U, B, logK=logK, exclude=[r for r, _ in cov]); ti = time.time() - t0
fm13.load(); fm = fm13.Members(N0, M, U)
lib = sv.lib; BL = 32768; nU = len(U)
bits = np.empty((nU, sv.words), dtype=np.uint64)
order, rank = np.empty(BL, dtype=np.uint32), np.empty(BL, dtype=np.uint32)
hs, selb = np.empty(nU + 2, dtype=np.uint32), np.empty(BL // 64, dtype=np.uint64)
ha, hk, at = ctypes.c_double(), ctypes.c_double(), ctypes.c_int64()
keep = int(math.ceil(BL * keepf))
Ts = Tsel = Tf = 0.0; tests = prps = cands = 0; mass = 0.0; hist = np.zeros(nU + 1, np.int64)
k0 = (kmax // 2) - (kmax // 2) % sv.K
for w in range(nwin):
    kw = k0 + w * sv.K
    t0 = time.process_time(); cnt, _ = sv.block(kw, bits=bits); Ts += time.process_time() - t0
    for b in range(0, sv.K, BL):
        cb = cnt[b:b + BL]
        t0 = time.process_time()
        n = lib.s200_select(cb.ctypes.data, BL, keep, nU, 0.07, order.ctypes.data, ctypes.byref(ha), ctypes.byref(hk), ctypes.byref(at), hs.ctypes.data)
        sel = order[:n]
        offs, cursor = np.empty(n + 1, np.int64), np.empty(n, np.int64)
        cap = int(cb[sel].astype(np.int64).sum()); rows = np.empty(max(cap, 1), np.uint16)
        lib.s200_csr(sv.ctx, bits.ctypes.data, ctypes.c_uint64(b // 64), BL, sel.ctypes.data, n, cb.ctypes.data, rank.ctypes.data,
                     selb.ctypes.data, cursor.ctypes.data, offs.ctypes.data, rows.ctypes.data, cap)
        Tsel += time.process_time() - t0
        hist += np.bincount(cb[sel], minlength=nU + 1)
        t0 = time.process_time(); fp = fm.first_pass(sel.astype(np.uint64) + np.uint64(kw + b), rows[:cap], offs); Tf += time.process_time() - t0
        tests += int(np.where(fp >= 0, fp + 1, np.diff(offs)).sum()); prps += int((fp >= 0).sum()); cands += int((fp < 0).sum())
m = nwin * sv.K
ph = prps / tests
mass = float((hist * (1 - ph) ** np.arange(len(hist))).sum())
tot = Ts + Tsel + Tf
print(f"B={B:.0e} logK={logK} keep={keepf}: init {ti:.1f}s; per member: sieve {Ts/m*1e6:.3f} us, select+rows {Tsel/m*1e6:.3f} us, "
      f"Fermat {Tf/m*1e6:.3f} us ({tests/m:.4f} tests a member, {Tf/tests*1e6:.2f} us a test); total {tot/m*1e6:.3f} us = "
      f"{m/tot:,.0f} members/s a core; p^={ph:.4f}, mean tested a {(hist*np.arange(len(hist))).sum()/hist.sum():.1f}, "
      f"expected hits {mass:.3e} in {m} members ({mass/tot:.3e} a core-second)", flush=True)
