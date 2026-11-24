# Markdown tables for README.md from t1_x*.json.   python3 make_tables.py > tables.md
import json, glob, math
G = {3000: 5.52, 10000: 6.53, 30000: 7.43, 100000: 8.38, 300000: 9.15}      # all-greedy G(x)/(x ln x), greedy_cover.txt
runs = sorted((json.load(open(f)) for f in glob.glob("t1_x*.json")), key=lambda d: d["x"])
f2 = lambda v: f"{v:.2f}"; f3 = lambda v: f"{v:.3f}"
print("### Report B: how far random small classes plus greedy large primes strike everything\n")
print("C* = the largest C (y = C·x·ln x) for which nothing is left in at least half of the draws (median of per-draw bisection).\n")
print("| x | w | large primes | C* increasing | C* decreasing | C* random | theorem | all-greedy G(x)/(x ln x) | ln x / ln ln x |")
print("|---|---|---|---|---|---|---|---|---|")
for d in runs:
    for wt, W in d["w"].items():
        B = W["B"]; cs = [f2(B[o]["C_star"]) if o in B else "–" for o in ("increasing", "decreasing", "random")]
        print(f"| {d['x']:,} | {wt} | {W['nB']:,} | " + " | ".join(cs) + f" | 1.349 | {G.get(d['x'], float('nan')):.2f} | {d['ln_x_over_lnln_x']:.2f} |")
print("\n### Report B: survivors struck per large prime (increasing order, mean over draws), and what is left\n")
print("| x | w | C | struck 0 | 1 | 2 | 3 | 4 | 5+ | left at the end | nothing left in |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for d in runs:
    for wt, W in d["w"].items():
        b = W["B"].get("increasing")
        if not b: continue
        for C in d["Cgrid"]:
            r = b[str(C)]; h = r["hist"]; tot = sum(h)
            cells = [f"{h[k]/tot:.3f}" for k in range(5)] + [f"{sum(h[5:])/tot:.3f}"]
            print(f"| {d['x']:,} | {wt} | {C} | " + " | ".join(cells) + f" | {r['left_mean']:.1f} | {r['nothing_left_frac']*100:.0f}% |")
print("\n### Report A: the counts the proof outline needs\n")
print("E = Σ_c C(n_c, 2) summed over the large primes (pairs of survivors in a common class), mean over draws. "
      "'balls' = the same count for |S| independent uniform balls in r − 1 boxes; 'exact' = the expectation over the random classes, "
      "computed from sampled target pairs (48 per large prime); 'r = 3 exact' = 0.5 · N₃ · ∏_{5 ≤ r ≤ w}(1 − 2/(r − 1)), with N₃ the target pairs "
      "in a common class of r′ that are also congruent mod 3. The formula as written, N · ∏_{3 ≤ r ≤ w}(1 − 2/(r − 1)), is 0 because of r = 3.\n")
print("| x | w | C | mean |S| | predicted | N / convexity | N₃ / N | E / exact | E / (r = 3 exact) | E / balls | ≥2 / Poisson | ≥3 / Poisson | ≥4 / Poisson | E² ratio | conflicts | good max (θ) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for d in runs:
    for wt, W in d["w"].items():
        for C in d["Cgrid"]:
            a = W["A"][str(C)]
            ex = a["E_mean"] / a["E_exact"] if a.get("E_exact") else float("nan")
            r3 = a["E_mean"] / a["E_naive_r3_exact"] if a.get("E_naive_r3_exact") and not math.isnan(a["E_naive_r3_exact"]) else float("nan")
            n3 = a["N3"] / a["N"] if a.get("N3") and not math.isnan(a["N3"]) else float("nan")
            nc = a["N"] / a["N_convexity"] if a["N_convexity"] > 0 else float("nan")
            print(f"| {d['x']:,} | {wt} | {C} | {a['S_mean']:,.0f} | {a['S_pred']:,.0f} | {nc:.2f} | {n3:.3f} | {ex:.3f} | {r3:.3f} | {a['E_mean']/a['E_balls']:.3f} | "
                  f"{a['c2']/a['c2_pois']:.3f} | {a['c3']/a['c3_pois']:.3f} | {a['c4']/a['c4_pois'] if a['c4_pois'] > 0 else float('nan'):.3f} | "
                  f"{a['second_moment_mean']:.4f} | {a['conflict_ratio_mean']:.3f} | {a['good_max']:.3f} ({a['good_argmax_theta']}) |")
print("\n### Report A (v): fraction of good large primes by θ\n")
th = runs[0]["thetas"]
print("| x | w | C | " + " | ".join(f"θ={t}" for t in th) + " |")
print("|---|---|---|" + "---|" * len(th))
for d in runs:
    for wt, W in d["w"].items():
        for C in d["Cgrid"]:
            if C not in (1.35, 2.0, 4.0): continue
            g = W["A"][str(C)]["good_frac"]
            print(f"| {d['x']:,} | {wt} | {C} | " + " | ".join(f"{v:.3f}" for v in g) + " |")
