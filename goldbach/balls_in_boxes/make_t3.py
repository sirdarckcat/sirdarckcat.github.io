# Markdown tables for T3.md from t3a.json, t3b_x*.json, t3c.json.   python3 make_t3.py > t3_tables.md
import json, glob, math
import numpy as np

A = json.load(open("t3a.json"))
print("### T3a: C*(x, θ), random nonzero classes up to w = x^θ, fullest class above w (increasing order)\n")
print("C* = the largest C (y = C·x·ln x) for which nothing is left: median of 10 draws, each a 14-step bisection on [0.25, 12]. "
      "θ = 0 is the all-greedy rule (one run; greedy_cover.txt has G(x)/(x ln x) = 6.53 and 8.38).\n")
print("| x | θ | w | random primes | C* | range over draws | C* / all-greedy | reach / (x ln² x) |")
print("|---|---|---|---|---|---|---|---|")
for x in sorted(A, key=int):
    X = int(x); L = math.log(X); c0 = float(np.median(A[x]["0.0"]))
    for th in sorted(A[x], key=float):
        v = np.array(A[x][th]); t = float(th); w = X ** t if t > 0 else 1
        nA = sum(1 for p in range(3, int(w) + 1, 2) if all(p % q for q in range(3, int(p ** 0.5) + 1, 2))) if t > 0 else 0
        rng = f"{v.min():.2f} – {v.max():.2f}" if len(v) > 1 else "one run"
        print(f"| {X:,} | {t} | {w:,.0f} | {nA:,} | {np.median(v):.3f} | {rng} | {np.median(v) / c0:.3f} | {np.median(v) / L:.3f} |")

E6 = json.load(open("t3a_x1000000.json")) if glob.glob("t3a_x1000000.json") else {}
if E6.get("0.0"):
    X = 1000000; L = math.log(X); c0 = E6["0.0"][0]["C"]
    for th in sorted(E6, key=float):
        v = np.array([r["C"] for r in E6[th]]); t = float(th); w = X ** t if t > 0 else 1
        P = np.arange(3, int(w) + 1, 2); sieve = np.ones(int(w) + 1, bool); sieve[:2] = False
        for p in range(2, int(w ** 0.5) + 1):
            if sieve[p]: sieve[p * p::p] = False
        nA = int(sieve[3:].sum()) if t > 0 else 0
        rng = f"{v.min():.2f} – {v.max():.2f}" if len(v) > 1 else "one run"
        print(f"| {X:,} | {t} | {w:,.0f} | {nA:,} | {np.median(v):.3f} | {rng} | {np.median(v) / c0:.3f} | {np.median(v) / L:.3f} |")
    print("\nAt x = 10^6 (`t3.py e`): 2 draws (θ > 0) or one run (θ = 0), 8 bisection steps inside a bracket around the predicted value "
          "(θ = 0: [9.9, 11]; 0.6: [8, 10.5]; 0.8: [5, 9]; 0.9: [3, 6]), so the resolution is 0.004 to 0.016.")
B = sorted((json.load(open(f)) for f in glob.glob("t3b_x*.json")), key=lambda d: d["x"])
print("\n### T3a against T3b: reach kept and the excess share of the random range\n")
print("s(θ) = share of the all-greedy excess Σ(m − λ) made by the primes up to x^θ (T3b run at the same x). "
      "At x = 10^6 the measured values come from `t3.py e` (2 draws per θ).\n")
print("| θ | x | s(θ) | 1 − s(θ) | C*(θ) / C*(0) measured |")
print("|---|---|---|---|---|")
T16 = json.load(open("t1_x1000000.json")) if glob.glob("t1_x1000000.json") else None
for th in ("0.2", "0.4", "0.6", "0.8", "0.9"):
    for d in B:
        x = d["x"]; sv = d["excess_share_below"][th]
        if str(x) in A: meas = f"{np.median(A[str(x)][th]) / np.median(A[str(x)]['0.0']):.3f}"
        elif x == 1000000 and E6.get("0.0") and (E6.get(th) or (th == "0.9" and T16)):
            c0 = E6["0.0"][0]["C"]
            cth = float(np.median([r["C"] for r in E6[th]])) if E6.get(th) else T16["w"]["x^0.9"]["B"]["increasing"]["C_star"]
            meas = f"{cth / c0:.3f}"
        elif x == 1000000 and th in ("0.2", "0.4"): meas = "not run"
        else: meas = "running"
        print(f"| {th} | {x:,} | {sv:.3f} | {1 - sv:.3f} | {meas} |")
print("\n### T3b: the all-greedy run, summary\n")
print("Targets = odd primes below y = 0.72 x ln² x; all primes up to x in increasing order, each taking its fullest nonzero class. "
      "λ = T/(r − 1) is the mean class size of what is left before r, m the class it takes; the excess is Σ(m − λ). "
      "'Random would leave' = T·∏(1 − 1/(p − 1)) over all odd p ≤ x, the expectation for random nonzero classes.\n")
print("| x | y | targets | left | excess / targets | random would leave | excess per prime | excess per prime / ln x |")
print("|---|---|---|---|---|---|---|---|")
for d in B:
    print(f"| {d['x']:,} | {d['y']:,} | {d['targets']:,} | {d['left']} | {d['excess_total'] / d['targets']:.3f} | {d['random_left_after_all'] / d['targets']:.3f} | "
          f"{d['excess_total'] / d['primes']:.2f} | {d['excess_total'] / d['primes'] / math.log(d['x']):.3f} |")
print("\n### T3b: by u = ln r / ln x, at three x\n")
print("Share of all strikes and of the excess made by the primes in each band; excess per prime; the targets left when the band starts, "
      "for the greedy run and for random classes at every prime, and their ratio.\n")
print("| u | x | primes | share of strikes | share of excess | excess per prime | per prime / ln x | left at start, greedy | left at start, random | greedy / random |")
print("|---|---|---|---|---|---|---|---|---|---|")
ub = {d["x"]: {(b["u_lo"]): b for b in d["ubins"]} for d in B}
for u in sorted(next(iter(ub.values()))):
    for d in B:
        b = ub[d["x"]].get(u)
        if not b: continue
        print(f"| {b['u_lo']:.1f}–{b['u_hi']:.1f} | {d['x']:,} | {b['primes']:,} | {b['strikes']:.3f} | {b['excess']:.3f} | {b['excess_per_prime']:.2f} | "
              f"{b['excess_per_prime'] / math.log(d['x']):.3f} | {b['left_before']:.4f} | {b['left_before_random']:.4f} | {b['gain']:.3f} |")
for d in B:
    if d["x"] != 100000: continue
    print(f"\n### T3b: profile of the all-greedy run at x = {d['x']:,}, y = {d['y']:,} (40 logarithmic bins in r)\n")
    print("m_max = E[fullest of r − 1 independent Poisson(λ) cells]. Ratios are means over the primes in the bin that still had targets; "
          "the last bin has 91 primes that came after everything was struck. 'Excess ratio' = (m − λ)/(m_max − λ): 1 means the class taken is as "
          "full as the fullest of independent cells. Shares are of all strikes and of the excess, with the running total.\n")
    print("| primes r | count | λ | m | m / λ | m / m_max | (m − λ)/√λ | excess ratio | √(ln r / ln y) | share of strikes (cum.) | share of excess (cum.) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    cs = ce = 0
    for r in d["rows"]:
        cs += r["share"]; ce += r["excess_share"]
        print(f"| {r['r_lo']:,}–{r['r_hi']:,} | {r['primes']:,} | {r['lam']:.4g} | {r['m']:.4g} | {r['m_over_lam']:.3f} | {r['m_over_mmax']:.3f} | {r['excess_sd']:.2f} | "
              f"{r['excess_ratio']:.3f} | {r['hooley']:.3f} | {r['share']:.4f} ({cs:.3f}) | {r['excess_share']:.4f} ({ce:.3f}) |")

C = json.load(open("t3c.json"))
for y in ("40111", "32971"):
    c = C[y]
    print(f"\n### T3c: the tempered 167-modulus cover against greedy on the same moduli, targets below {int(y):,} ({c['targets']:,})\n")
    print(f"Tempered vector (the 40,111 cover), moduli in increasing order: {c['left_tempered']} left. Greedy on the same moduli: {c['left_greedy']} left. "
          "'Taken / fullest' compares the tempered class with the fullest nonzero class of what is left at that point of the tempered path.\n")
    print("| moduli r | count | tempered λ | tempered m | tempered m / m_max | greedy λ | greedy m | greedy m / m_max | tempered taken / fullest | tempered takes the fullest |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for t, g in zip(c["tempered"], c["greedy"]):
        print(f"| {t['r_lo']:,}–{t['r_hi']:,} | {t['primes']} | {t['lam']:.3g} | {t['m']:.3g} | {t['m_over_mmax']:.3f} | {g['lam']:.3g} | {g['m']:.3g} | {g['m_over_mmax']:.3f} | "
              f"{t['taken_over_fullest']:.3f} | {t['fullest_taken']:.0%} |")
