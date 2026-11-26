import math, sys
from compare1 import mine
def levels(q, n):
    hdr, gh, gh0, dh, dh0, top, lst = mine(q, n); tot = q ** n
    out = []; surv = tot; gs = sorted(gh); cum = {}
    s = 0
    for g in sorted(gh, reverse=True): s += gh[g]; cum[g] = s
    def A(g): return sum(c for gg, c in gh.items() if gg >= g)
    for k in range(1, 7):
        g = 0
        while A(g) >= tot * 10.0 ** (-k): g += 1
        out.append(g)
    return out, hdr, gh, top
if __name__ == "__main__":
    for q, n in [(3,16),(5,11),(7,9),(9,8),(3,18),(3,12),(3,15),(5,10),(7,7),(9,6)]:
        lv, hdr, gh, top = levels(q, n); tot = q ** n; rho = hdr["irr_n"] / tot
        Gmax = max(gh); naive = math.log(tot) / -math.log(1 - rho)
        print(q, n, "levels", lv, "Gmax", Gmax, "naive max %.1f" % naive, "top:", top[:3])
