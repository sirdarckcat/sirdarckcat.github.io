# Checks of the C kernels against plain Python on small inputs.
import math, numpy as np, t1
L = t1.L_(); rng = np.random.default_rng(5)
P = t1.primes_upto(200000)
# 1. occupancy
S = np.sort(rng.choice(P, 3000, replace=False)).astype(np.uint32); B = P[(P > 500) & (P < 900)]
E, c2, c3, c4 = t1.occupancy(S, B, 4)
for i, r in enumerate(B.tolist()):
    n = np.bincount(S % r, minlength=r)
    assert abs(E[i] - (n * (n - 1) / 2).sum()) < 1e-9 and c2[i] == (n >= 2).sum() and c3[i] == (n >= 3).sum() and c4[i] == (n >= 4).sum()
print("occupancy ok")
# 2. conflicts, by brute force over pairs
S2 = S[:600]; R1 = np.array([503, 601, 701], np.uint32); R2 = np.array([509, 607, 887], np.uint32); X = np.zeros(3)
L.conflicts(S2, len(S2), R1, R2, 3, X, 2)
for i in range(3):
    p1 = [(a, b) for a in range(len(S2)) for b in range(a + 1, len(S2)) if S2[a] % R1[i] == S2[b] % R1[i]]
    p2 = [(a, b) for a in range(len(S2)) for b in range(a + 1, len(S2)) if S2[a] % R2[i] == S2[b] % R2[i]]
    xb = sum(1 for u in p1 for v in p2 if set(u) & set(v))
    assert xb == X[i], (xb, X[i])
print("conflicts ok")
# 3. greedy against numpy, same tie rule (smallest nonzero class among the fullest)
def greedy_py(S, B):
    S = S.astype(np.int64); st = []
    for r in B.tolist():
        if len(S) == 0: st.append(0); continue
        res = S % r; cnt = np.bincount(res, minlength=r); cnt[0] = 0; a = int(np.argmax(cnt))
        st.append(int((res == a).sum())); S = S[res != a]
    return len(S), np.array(st)
for Bo in (B, B[::-1].copy()):
    left, st = t1.greedy_job((S, np.ascontiguousarray(Bo)))
    l2, st2 = greedy_py(S, Bo)
    assert left == l2 and (st == st2).all()
print("greedy ok")
# 4. survivors against a direct check
A = P[P <= 97]; a = (rng.integers(0, A.astype(np.int64) - 1) + 1)
Sv = t1.survivors(P, A, a, 200000)
direct = np.array([q for q in P.tolist() if all(q % r != ar for r, ar in zip(A.tolist(), a.tolist()))])
assert (Sv == direct).all()
print("survivors ok")
# 5. exact expectation of E_r against Monte Carlo
x, w, C = 400, 200, 4.0; y = C * x * math.log(x); T = P[P <= y]; A = P[P <= w]; Bx = P[(P > w) & (P <= x)]
Nx = np.zeros(len(Bx)); Pb = np.zeros(len(Bx)); L.exact_pairs(T, len(T), Bx, len(Bx), A, len(A), 4000, 9, Nx, Pb, 4)
mc = np.zeros(len(Bx)); D = 3000
for d in range(D):
    a = rng.integers(0, A.astype(np.int64) - 1) + 1
    mc += t1.occupancy(t1.survivors(T, A, a, int(y) + 1), Bx, 4)[0]
mc /= D
print(f"exact E (sum over r) {(Nx*Pb).sum():.2f} against Monte Carlo {mc.sum():.2f} over {D} draws")
assert abs((Nx * Pb).sum() / mc.sum() - 1) < 0.03
# 6. deletion: marked pairs per prime ~ theta, primes with one marked pair ~ theta e^-theta, good <= one (20 seeds, 191 primes)
x, w, C = 3000, 1500, 4.0; y = C * x * math.log(x); T = P[P <= y]; A = P[P <= w]; Bx = P[(P > w) & (P <= x)]
a = rng.integers(0, A.astype(np.int64) - 1) + 1; Sx = t1.survivors(T, A, a, int(y) + 1)
th = np.array([0.1, 0.5, 1.0, 2.0]); Ed = t1.occupancy(Sx, Bx, 4)[0]
G = np.zeros(4); O = np.zeros(4); Mk = np.zeros(4)
for seed in range(20):
    g = np.zeros(4, np.int64); o = np.zeros(4, np.int64); m = np.zeros(4, np.int64)
    L.deletion(Sx, len(Sx), Bx, len(Bx), np.ascontiguousarray(Ed), th, 4, seed, g, o, m, 4)
    assert (g <= o).all(); G += g; O += o; Mk += m
n = 20 * len(Bx)
print("deletion: marked/prime", Mk / n, "one/prime", O / n, "Poisson", th * np.exp(-th), "good/prime", G / n)
assert np.allclose(Mk / n, th, rtol=0.1) and np.allclose(O / n, th * np.exp(-th), rtol=0.15)
print("all checks passed")
