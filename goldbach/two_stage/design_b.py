# Question (b) of the lead's split, for the research session (25 November): the best two-stage design at 200 digits.
# The stages are sieve depth B, window W and keep fraction kappa, with an optional staged sieve (a funnel); the yield is in nats
# against the present single cut (B = 1e8, W = 2^24, keep 1.5%).
#
# Model. The numbers below are the research session's.
#   - Rows R = 1,502, each prime with probability p = 0.02398 before the sieve; 89 moduli, the odd primes up to X = 463.
#   - At depth B a row survives with probability c(B) = prod over X < s <= B of (1 - 1/s), about 1.0019 ln X/ln B. A survivor is
#     prime with probability p'(B) = p/c(B).
#   - The survivor count S is about normal(R c, sigma^2), with sigma = 0.962 sqrt(R c (1 - c)): sub-binomial, from the pair structure
#     of the rows.
#   - A member is a hit with probability (1 - p')^S = e^(-lambda S), lambda = -ln(1 - p'). So the hit-weighted law of S is the
#     same normal shifted down by lambda sigma^2, which is delta = lambda sigma standard deviations.
#   - Keeping the members with S <= mu + z sigma (kappa = Phi(z)) captures Phi(z + delta) of the hit mass.
#   - Work per member: w_s (the sieve) + kappa w_t (the tests). A kept member costs w_t = (1 - (1-p')^S)/p', about 1/p' Fermat tests,
#     whatever its S.
#   - Hits per unit work: eta = P_hit Phi(z + delta) / (w_s + Phi(z) w_t). P_hit = (1 - p)^R does not depend on B, W or kappa.
#   - Constants are not known yet, so everything is in units of w_t at the present depth. rho = w_s/w_t at the present design;
#     phi = the share of w_s spent on per-vector set-up (start positions, R pi(B) per window). The rest is marks
#     (R ln(ln B/ln X) per member).
#   python3 design_b.py
import math
from math import erf, exp, log, sqrt

def Phi(z): return 0.5 * (1 + erf(z / sqrt(2)))
def Phinv(u):
    lo, hi = -12.0, 12.0
    for _ in range(100):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if Phi(m) < u else (lo, m)
    return (lo + hi) / 2
def pi_approx(x): return x / (log(x) - 1.08)

R, P, X = 1502, 0.02398, 463
B0, W0, KAPPA0 = 1e8, 2 ** 24, 0.015
SUB = 0.962

def stats(B):
    c = 1.0019 * log(X) / log(B); pp = P / c; lam = -log(1 - pp)
    sigma = SUB * sqrt(R * c * (1 - c))
    return c, pp, lam, sigma, lam * sigma

def best_z(rho_s, wt, delta):
    """max over z of Phi(z + delta) / (rho_s + Phi(z) wt): golden-section search on z in [-8, 6], then a check of the ends."""
    f = lambda z: Phi(z + delta) / (rho_s + Phi(z) * wt)
    a, b = -8.0, 6.0; g = (sqrt(5) - 1) / 2
    for _ in range(200):
        c1, c2 = b - g * (b - a), a + g * (b - a)
        if f(c1) < f(c2): a = c1
        else: b = c2
    z = (a + b) / 2
    return max([(f(z), z), (f(6.0), 6.0)])

def sieve_cost(B, W, rho0, phi):
    """w_s relative to w_t at the present design: marks scale with ln(ln B/ln X), set-up with pi(B)/W."""
    M0 = log(log(B0) / log(X)); M = log(log(B) / log(X))
    return rho0 * ((1 - phi) * M / M0 + phi * (pi_approx(B) / pi_approx(B0)) * (W0 / W))

if __name__ == "__main__":
    c0, pp0, lam0, sig0, d0 = stats(B0)
    z0 = Phinv(KAPPA0)
    print(f"present design: B = 1e8, W = 2^24, keep 1.5% (z = {z0:.3f}). c = {c0:.4f}, p' = {pp0:.4f} (1/p' = {1/pp0:.1f} tests a kept member), "
          f"sigma = {sig0:.2f}, delta = lambda sigma = {d0:.3f} (p' sigma = {pp0 * sig0:.3f})")
    print(f"  hit mass captured at 1.5%: Phi(z + delta) = {Phi(z0 + d0):.3f} (with p' sigma instead of lambda sigma: {Phi(z0 + pp0 * sig0):.3f})")
    # rho at which the present cut is the optimum: phi(z+d)(rho + Phi(z)) = Phi(z+d) phi(z)  ->  rho = Phi(z+d) e^{z d + d^2/2} - Phi(z)
    rho_star = Phi(z0 + d0) * exp(z0 * d0 + d0 * d0 / 2) - Phi(z0)
    print(f"  the present keep fraction is optimal exactly when rho = sieve cost per member / test cost per kept member = {rho_star:.4f}")
    print("\n(1) the keep fraction alone (B and W as now): optimum and gain over keeping 1.5%")
    print("   rho      best keep   hit mass   gain (nats)")
    for rho in (1e-4, 3e-4, 1e-3, 3e-3, 0.01, rho_star, 0.02, 0.03, 0.05, 0.1, 0.2, 0.5, 1.0, 3.0):
        e_opt, z = best_z(rho, 1.0, d0)
        e_now = Phi(z0 + d0) / (rho + KAPPA0)
        print(f"   {rho:7.4f}  {100 * Phi(z):8.3f}%  {100 * Phi(z + d0):7.1f}%   {log(e_opt / e_now):.3f}")
    print("\n(2) depth B, window W and keep fraction together (W up to 2^30, the members of one cover): gain over the present design")
    Bs = [10 ** (e / 4) for e in range(24, 45)]; Ws = [2 ** k for k in range(20, 31)]
    for phi in (0.2, 0.5, 0.8):
        print(f"   set-up share phi = {phi} of the present sieve cost")
        for rho in (0.003, 0.01, 0.03, 0.1, 0.3, 1.0):
            e_now = Phi(z0 + d0) / (rho + KAPPA0)
            best = None
            for B in Bs:
                c, pp, lam, sig, d = stats(B); wt = (1 / pp) / (1 / pp0)
                for W in Ws:
                    ws = sieve_cost(B, W, rho, phi)
                    e, z = best_z(ws, wt, d)
                    if best is None or e > best[0]: best = (e, B, W, z, d)
            # with the window fixed at 2^24
            bestW = None
            for B in Bs:
                c, pp, lam, sig, d = stats(B); wt = (1 / pp) / (1 / pp0)
                ws = sieve_cost(B, W0, rho, phi); e, z = best_z(ws, wt, d)
                if bestW is None or e > bestW[0]: bestW = (e, B, z)
            e, B, W, z, d = best
            print(f"     rho {rho:5.3f}: W = 2^24: best B = {bestW[1]:.1e}, keep {100 * Phi(bestW[2]):.2f}%, gain {log(bestW[0] / e_now):.3f} nats | "
                  f"any W: B = {B:.1e}, W = 2^{int(round(log(W, 2)))}, keep {100 * Phi(z):.2f}%, gain {log(e / e_now):.3f} nats")

    print("\n(3) the window alone, at rho = 0.0118 (where 1.5% is optimal now) and phi = 0.5: B and keep re-optimized for each W")
    for k in (22, 24, 26, 28, 30):
        W = 2 ** k; e_now = Phi(z0 + d0) / (rho_star + KAPPA0); best = None
        for B in Bs:
            c, pp, lam, sig, d = stats(B); wt = (1 / pp) / (1 / pp0)
            e, z = best_z(sieve_cost(B, W, rho_star, 0.5), wt, d)
            if best is None or e > best[0]: best = (e, B, z)
        print(f"   W = 2^{k}: best B = {best[1]:.1e}, keep {100 * Phi(best[2]):.2f}%, gain {log(best[0] / e_now):+.3f} nats")
    print("\n(4) a staged sieve (funnel): continuing one kept member from depth B1 to B2 by itself costs one reduction of N mod s for each")
    print("    prime s in (B1, B2]. That is tau = (reduction)/(Fermat test) of a test each, with tau ~ 1e-4 at 664 bits by word counts:")
    print("    about 11 word divisions for a reduction against about 664*(2*11^2) multiply-adds for a test. Testing the member at B1")
    print("    instead costs 1/p'(B1) tests. Continuation is worth it only if pi(B2) - pi(B1) < (1/p'(B1))/tau primes:")
    for B1 in (1e6, 1e7, 1e8):
        c, pp, lam, sig, d = stats(B1)
        for tau in (1e-3, 1e-4):
            lim = (1 / pp) / tau
            print(f"   B1 = {B1:.0e}: 1/p' = {1 / pp:.1f}; with tau = {tau:g}, continuing beats testing only over fewer than {lim:,.0f} primes, "
                  f"i.e. to B2 = B1 + about {lim * log(B1):,.0f} (c changes by {100 * (1 - log(B1) / log(B1 + lim * log(B1))):.3f}%)")
