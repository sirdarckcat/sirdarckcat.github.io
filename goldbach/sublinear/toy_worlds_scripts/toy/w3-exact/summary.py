# One line per completely enumerated instance, from the pass-1 files.
import glob, re, math
from tail import load, survival
print("q n | q^n | rows(deg<n) | Gmax (#N) second | Dmax (#N) | exceptions | mean G | naive max g = ln(q^n)/-ln(1-rho) | naive E#{G>=Gmax} = q^n(1-rho)^Gmax | rows of degree < Dmax | naive E#{D>=Dmax}")
for fn in sorted(glob.glob("out_*_*.txt"), key=lambda s: tuple(int(t) for t in re.findall(r"\d+", s)[-2:])):
    q, n, H, info = load(fn); tot = q ** n; A = survival(H); gs = sorted(H, reverse=True)
    rho = info["rho"][0][0]; rb = info["rb"]; Dmax = info["Dmax"]
    mean = sum(g * c for g, c in H.items()) / tot
    print(f"{q} {n:>2} | {tot:>10} | {rb[n]:>8} | {gs[0]:>4} ({H[gs[0]]}) {gs[1]:>4} | {Dmax} ({info['nD']}) | {info['exc']} | {mean:6.2f} | {math.log(tot) / -math.log(1 - rho):6.1f} |"
          f" {tot * (1 - rho) ** gs[0]:.3g} | {rb[Dmax] if Dmax < n else rb[n]} | {tot * (1 - rho) ** (rb[Dmax] if Dmax < n else rb[n]):.3g}")
