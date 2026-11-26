# (b) for the research session: covers tempered for a weighted target (rows below 170,000 weigh 1, rows in [170,000, 200,000) weigh w;
# heatbath_w.c, 20,000 sweeps; the 463 family from the 170,000 and 200,000 covers, three seeds each, and the fleet's 491 family from
# its 170,000 cover, four seeds; the best kept), put through campaign_table.py's
# model with every tested member's g counted, the budget calibrated on the 170,000 cover the fleet runs, the cut at 170,000.
# With --cuts, every cover (the weighted ones and the 180,000-200,000 designs) is also run with the cut (the sieve and the 1.5%
# selection on the rows below it) at 170,000-200,000, and the best (cover, cut) is printed for each x.
#   python3 weighted_eval.py [package_nats] [--cuts]
import sys, importlib.util
spec = importlib.util.spec_from_file_location("ct", "campaign_table.py"); ct = importlib.util.module_from_spec(spec); spec.loader.exec_module(ct)
args = [a for a in sys.argv[1:] if a != "--cuts"]; pk = float(args[0]) if args else 0.0
ref = (170000, "q170000_m89r491", 5.5)
cases = [("170,000 cover (the fleet's)", ref)]
for fam, suffix in (("491 family", "_m89r491"), ("463 family", "_m89")):
    for w, f in (("0.25", "qw025"), ("0.5", "qw05"), ("0.75", "qw075")):
        cases.append((f"w = {w} ({fam}), cut at 170,000", (170000, f + suffix, 5.5 if suffix == "_m89r491" else 4.5)))
cases.append(("200,000 cover, cut at 200,000", (200000, "q200000_m89", 4.5)))
xs = list(range(165000, 200001, 5000))
print(f"engineering package {pk:+.2f} nats; budget 1.90 design hits at 170,000 on the fleet's cover; floor 160,357; every tested member's g counted")
print("design | rows below 170k (run) | rows below 200k (run) | E[record] | " + " | ".join(f"P(>= {x // 1000}k)" for x in xs))
for name, d in cases:
    ct.DESIGNS = [ref, d]
    row = ct.table(pk)[-1]
    U, C, c = ct.load(d[1]); nb = int((U < d[0]).sum()); sc = (nb + d[2]) / nb
    print(f"{name} | {(U < 170000).sum() * sc:.0f} | {(U < 200000).sum() * sc:.0f} | {row[9]:,.0f} | " + " | ".join(f"{100 * row[10][x]:.2f}%" for x in xs))

if "--cuts" in sys.argv:
    covers = [("the fleet's 170,000 cover", "q170000_m89r491", 5.5)] + [(f"w = {w} ({fam})", f + sfx, ex)
              for fam, sfx, ex in (("491 family", "_m89r491", 5.5), ("463 family", "_m89", 4.5))
              for w, f in (("0.5", "qw05"), ("0.75", "qw075"))] + [(f"{D // 1000},000 design", f"q{D}_m89", 4.5) for D in (180000, 190000, 200000)]
    res = []
    print("cut sweep: every cover with the cut at 170,000-200,000")
    print("cover | cut | E[record] | " + " | ".join(f"P(>= {x // 1000}k)" for x in xs))
    for name, f, ex in covers:
        for D in range(170000, 200001, 5000):
            ct.DESIGNS = [ref, (D, f, ex)]; row = ct.table(pk)[-1]; res.append((name, D, row[9], row[10]))
            print(f"{name} | {D:,} | {row[9]:,.0f} | " + " | ".join(f"{100 * row[10][x]:.2f}%" for x in xs))
    print("best (cover, cut) for each x:")
    for x in xs:
        b = max(res, key=lambda r: r[3][x]); print(f"  P(>= {x:,}): {b[0]}, cut {b[1]:,}: {100 * b[3][x]:.2f}% (E[record] {b[2]:,.0f})")
    b = max(res, key=lambda r: r[2]); print(f"  E[record]: {b[0]}, cut {b[1]:,}: {b[2]:,.0f}")
