# Item 3 (research, 25 Nov): the keep fraction when the objective is the expected final record with every tested member's g
# counted, not design hits. The campaign model of ../campaign_table.py (the fleet's 170,000 cover, rows as run +5.5, budget
# 1.90 design hits at 170,000 as the fleet runs at keep 1.5%, floor 160,357), with the keep kappa free:
#   below the design level  Lam(G) = M e^-E(n_G) Phi(z_kappa + lam' sd(n_G)^2 / sd(n_D)),
#   at and above it         Lam(G) = M e^-E(n_D) Phi(z_kappa + lam' sd(n_D)) e^(-lam (rows in [D, G))),
#   M = W / cost(kappa), W fixed by the calibration at kappa = 1.5%.
# Three costs of a member as a function of the keep:
#   (A) additive, the campaign model's split: 0.26 + 0.74 kappa / 0.015;
#   (B) the G4 pipeline (both at once: Fermat at 0.735, sieve at 0.43 of solo speed; Fermat-only 1.318 s and sieve 0.434 s a
#       batch at keep 1.5%, GPU session via uarch), rounds as now: the Fermat bulk scales with the kept members and with
#       1 / (1 - waste(kappa)), waste from item2_carry.py's recursion (half-pools of 503,808 kappa / 1.5% members, T = 2^18), plus
#       a fixed tail of 0.175 s a batch (t_min 4 ms);
#   (C) the same with carry-over: no waste, no tail.
# The batch time of the pipeline is F + S (1 - 0.735) / 0.43 when Fermat-bound, S + F (1 - 0.43) / 0.735 when sieve-bound.
#   python3 item3_keep.py
import sys, math, importlib.util, os
import numpy as np
from statistics import NormalDist
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ct", os.path.join(here, "..", "campaign_table.py")); ct = importlib.util.module_from_spec(spec)
cwd = os.getcwd(); os.chdir(os.path.join(here, "..")); spec.loader.exec_module(ct)
sys.path.insert(0, here); import item2_carry as i2
ND = NormalDist()

D, f, extra_run = 170000, "q170000_m89r491", 5.5
U, C, c = ct.load(f); os.chdir(cwd)
nbest = int((U < D).sum()); scale = (nbest + extra_run) / nbest
p = C / ct.L; lamp = -math.log1p(-p / c); lam = -math.log1p(-p)
n_below = lambda G: float((U < G).sum()) * scale
sdv = lambda n: 0.9836 * math.sqrt(n * c * (1 - c))
nD = n_below(D); E_D = ct.window_E(nD, C); dD = lamp * sdv(nD)
K0 = 0.015
W_hits = 1.90 / (math.exp(-E_D) * ND.cdf(ND.inv_cdf(K0) + dD))     # members (in cost units of the fleet as run) of the budget

def waste(kappa):
    P = max(1000, int(503808 * kappa / K0)); cmp, use, _, _ = i2.pool_no_carry(P, 2 ** 18, 0.0715); return (cmp - use) / cmp
W15 = waste(K0)
def batch(F, S, rf=0.735, rs=0.43):
    ts, tf = S / rs, F / rf
    return F + S * (1 - rf) / rs if ts <= tf else S + F * (1 - rs) / rf
F15, S0, TAIL = 1.318, 0.434, 0.175
def cost(kappa, model):
    if model == "A": return 0.26 + 0.74 * kappa / K0
    bulk = (F15 - TAIL) * (1 - W15) * kappa / K0                       # the useful Fermat work
    if model == "B": F = bulk / (1 - waste(kappa)) + TAIL
    else: F = bulk                                                      # C: carry-over
    return batch(F, S0) / batch(F15, S0)                                # today's batch = 1

def forecast(kappa, model, package=0.0):
    M = W_hits * math.exp(package) / cost(kappa, model); z = ND.inv_cdf(kappa)
    def Lam(G):
        if G >= D:
            extra = float(((U >= D) & (U < G)).sum()) * scale
            return M * math.exp(-E_D) * ND.cdf(z + dD) * math.exp(-extra * lam)
        nG = n_below(G); return M * math.exp(-ct.window_E(nG, C)) * ND.cdf(z + lamp * sdv(nG) ** 2 / sdv(nD))
    grid = np.arange(ct.R0, 400001, 250)
    P = np.array([1 - math.exp(-Lam(G)) for G in grid])
    return dict(E=ct.R0 + float(P.sum()) * 250, hits=Lam(D), **{f"P{x // 1000}": 1 - math.exp(-Lam(x)) for x in (170000, 180000, 190000, 200000)})

if __name__ == "__main__":
    ks = [0.0025, 0.004, 0.005, 0.006, 0.0075, 0.01, 0.0125, 0.015, 0.02, 0.025, 0.03]
    print(f"waste without carry-over (item 2's recursion): " + ", ".join(f"{100 * k:.2f}% keep: {100 * waste(k):.2f}%" for k in (0.005, 0.0075, 0.015, 0.03)))
    for model, name in (("A", "(A) additive 0.26 + 0.74 kappa/1.5%"), ("B", "(B) G4 pipeline, rounds as now"), ("C", "(C) G4 pipeline, carry-over")):
        print(f"\n{name}: cost of a member against today")
        print("keep | cost | design hits at 170k | E[final record] | P(>= 180k) | P(>= 190k) | P(>= 200k)")
        rows = []
        for k in ks:
            r = forecast(k, model); rows.append((k, r))
            print(f"{100 * k:.2f}% | {cost(k, model):.3f} | {r['hits']:.3f} | {r['E']:,.0f} | {100 * r['P180']:.2f}% | {100 * r['P190']:.3f}% | {100 * r['P200']:.3f}%")
        # finer optimum
        fine = np.exp(np.linspace(np.log(0.002), np.log(0.04), 200))
        bestE = max(fine, key=lambda k: forecast(k, model)["E"]); bestH = max(fine, key=lambda k: forecast(k, model)["hits"])
        rE = forecast(bestE, model); r15 = forecast(K0, model)
        flat = [k for k in fine if forecast(k, model)["E"] >= rE["E"] - 100]
        print(f"  optimum for E[final record]: keep {100 * bestE:.2f}% (E {rE['E']:,.0f}; at 1.5%: {r15['E']:,.0f}, {r15['E'] - rE['E']:+,.0f}); within 100 of it: {100 * min(flat):.2f}%-{100 * max(flat):.2f}%")
        print(f"  optimum for design hits:     keep {100 * bestH:.2f}% ({forecast(bestH, model)['hits']:.3f} against {r15['hits']:.3f} at 1.5%: {math.log(forecast(bestH, model)['hits'] / r15['hits']):+.3f} nats)")
