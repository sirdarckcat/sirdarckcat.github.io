# A complete toy of the search over F_3[x]: cover, members, sieve, selection, tests -- with and without the parity
# filter that exists in this setting (Stickelberger-Swan: for squarefree f of degree n over F_q, q odd, the number r
# of irreducible factors satisfies chi(disc f) = (-1)^(n - r); so "r odd", which irreducibility needs, is read off a
# discriminant).
#
#   python3 toy_search.py [m=4] [gdeg=8] [tau=9] [zdeg=6] [seed=1] [members=0]      (members > 0: that many random T)
#
# Rows: monic irreducible Q of degree <= gdeg.  Cover: every irreducible of degree <= m gets a class (greedy).
# Members: N = N0 + T*M, T monic of degree tau (3^tau members).  A member succeeds when N - Q is reducible for all rows.
# Sieve: a row "survives" when N - Q has no irreducible factor of degree in (m, zdeg].
import itertools, math, random, sys, time
from flint import nmod_poly, fq_default_ctx, fq_default_poly_ctx

P = 3
m = int(sys.argv[1]) if len(sys.argv) > 1 else 4
gdeg = int(sys.argv[2]) if len(sys.argv) > 2 else 8
tau = int(sys.argv[3]) if len(sys.argv) > 3 else 9
zdeg = int(sys.argv[4]) if len(sys.argv) > 4 else 6
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
nmem = int(sys.argv[6]) if len(sys.argv) > 6 else 0
F = fq_default_ctx(P, 1); R = fq_default_poly_ctx(F)
X = nmod_poly([0, 1], P)
def is_irr(f): return R([int(c) for c in f.coeffs()]).is_irreducible()
def monics(d):
    for c in itertools.product(range(P), repeat=d): yield nmod_poly(list(c) + [1], P)
irr = {d: [f for f in monics(d) if is_irr(f)] for d in range(1, gdeg + 1)}
rows = [Q for d in range(1, gdeg + 1) for Q in irr[d]]
moduli = [pi for d in range(1, m + 1) for pi in irr[d]]
# greedy cover
key = lambda f: tuple(int(c) for c in f.coeffs())
uncovered = set(range(len(rows))); cover = []
for pi in moduli:
    cls = {}
    for i in uncovered: cls.setdefault(key(rows[i] % pi), []).append(i)
    best = max(cls.items(), key=lambda kv: len(kv[1])) if cls else ((1,), [])
    cover.append((pi, nmod_poly(list(best[0]), P))); uncovered -= set(best[1])
U = [rows[i] for i in sorted(uncovered)]
# CRT
N0 = nmod_poly([0], P); M = nmod_poly([1], P)
for pi, a in cover:
    g, s, t = (M % pi).xgcd(pi)
    assert g.degree() == 0
    sinv = s * nmod_poly([pow(int(g.coeffs()[0]), -1, P)], P)
    N0 = N0 + M * (((a - N0 % pi) * sinv) % pi); M = M * pi
assert all((N0 - a) % pi == 0 for pi, a in cover)
boost = 1.0
for pi, _ in cover: boost /= 1 - P ** -pi.degree()
n = M.degree() + tau
p0 = boost / n
print(f"F_3: {len(rows)} rows of degree <= {gdeg}; cover on the {len(moduli)} irreducibles of degree <= {m} (deg M = {M.degree()}) leaves "
      f"{len(U)} rows; members N0 + T*M, T monic of degree {tau}: {nmem or P**tau} members of degree {n}; p0 = boost/n = {p0:.4f}, E = {len(U)*p0:.2f}")
# sieve: f has an irreducible factor of degree j exactly when gcd(f, x^(3^j) - x) is not constant (f coprime to lower degrees)
def pow_mod3(h, f): return (h * h % f) * h % f
def survives(f):
    h = X % f
    for j in range(1, zdeg + 1):
        h = pow_mod3(h, f)
        if j > m and (h - X).gcd(f).degree() > 0: return False
    return True
rng = random.Random(seed)
if nmem: members = [tuple(rng.randrange(P) for _ in range(tau)) for _ in range(nmem)]
else: members = list(itertools.product(range(P), repeat=tau)); rng.shuffle(members)
want_odd = (n - 1) % 2            # r odd  <=>  chi(disc) = (-1)^(n-1)
rec = []; t0 = time.time(); stats = dict(rows=0, surv=0, odd=0, odd_surv=0, irr=0, irr_odd=0, irr_even=0, nonsqf=0)
for c in members:
    N = N0 + nmod_poly(list(c) + [1], P) * M
    nsurv = nodd = nirr = 0; order = []
    for Q in U:
        f = N - Q
        d = int(f.discriminant())
        if d == 0: stats["nonsqf"] += 1; par_odd = False
        else: par_odd = ((0 if d == 1 else 1) == want_odd)        # chi(1) = +1, chi(2) = -1 in F_3
        s = survives(f)
        stats["rows"] += 1; stats["odd"] += par_odd
        if s:
            ir = is_irr(f)
            stats["surv"] += 1; stats["odd_surv"] += par_odd; stats["irr"] += ir
            stats["irr_odd"] += ir and par_odd; stats["irr_even"] += ir and not par_odd
            nsurv += 1; nodd += par_odd; nirr += ir; order.append((par_odd, ir))
    rng.shuffle(order)
    ta = next((i + 1 for i, (_, ir) in enumerate(order) if ir), len(order))                 # tests, all survivors
    odd_only = [ir for po, ir in order if po]
    tb = next((i + 1 for i, ir in enumerate(odd_only) if ir), len(odd_only))               # tests, odd survivors only
    rec.append((nsurv, nodd, nirr == 0, ta, tb))
dt = time.time() - t0
S = stats; nm = len(rec); succ = sum(r[2] for r in rec)
print(f"{nm} members in {dt:.0f} s; successes {succ} ({succ/nm:.5f}; (1-p0)^k = {(1-p0)**len(U):.5f})")
print(f"rows surviving the sieve to degree {zdeg}: {S['surv']/S['rows']:.3f} of the uncovered rows; irreducible among survivors p_z = {S['irr']/S['surv']:.4f}")
print(f"odd parity among all uncovered rows {S['odd']/S['rows']:.4f}, among survivors {S['odd_surv']/S['surv']:.4f}; "
      f"irreducible with even parity: {S['irr_even']} (must be 0); P(irreducible | survivor, odd) = {S['irr_odd']/max(S['odd_surv'],1):.4f}; not squarefree {S['nonsqf']}")
def curve(idx, name, tcol):
    order = sorted(rec, key=lambda r: (r[idx], rng.random()))
    print(f"selection by {name}: fraction kept | share of all successes | tests per kept member | successes per 1000 tests")
    for f in (0.01, 0.03, 0.1, 0.3, 1.0):
        kept = order[:max(1, int(f * nm))]
        s = sum(r[2] for r in kept); t = sum(r[tcol] for r in kept)
        print(f"   {f:5.2f} | {s/max(succ,1):.3f} | {t/len(kept):6.2f} | {1000*s/max(t,1):.3f}")
curve(0, "rows left after the sieve (as in production), testing all survivors", 3)
curve(1, "ODD rows left after the sieve, testing only the odd ones", 4)
