# survival function A_g = #{N : G(N) >= g}; levels with A_g/q^n <= 10^-k; slope of ln A_g; first-moment predictions
import sys, re, math, collections
def load(fn):
    q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:]); H = collections.Counter(); info = {}
    for line in open(fn):
        t = line.split()
        if t[0] == "GH" and int(t[1]) <= n: H[int(t[2])] += int(t[3])
        if t[0] == "q": info["nirr"] = int(t[t.index("n:") + 1]) if "n:" in t else None; info["head"] = line
        if t[0] == "rows_below:": info["rb"] = [0] + [int(v) for v in t[1:]]
        if t[0] == "threshold": info.setdefault("rho", {})[int(t[1])] = (float(t[-2].split("=")[1]), float(t[-1].split("=")[1]), t[3] if False else line.split("(")[1].split(")")[0], int(t[2].split("=")[1]))
        if t[0] == "Gmax": info["Gmax"] = int(t[1]); info["Dmax"] = int(t[3]); info["nD"] = int(t[5]); info["exc"] = int(t[-1])
    return q, n, H, info
def survival(H):
    A = {}; tot = 0
    for g in sorted(H, reverse=True): tot += H[g]; A[g] = tot
    return A
if __name__ == "__main__":
    q, n, H, info = load(sys.argv[1]); A = survival(H); tot = q ** n; gs = sorted(A)
    rho = info["rho"][0][0]
    print(f"q={q} n={n} N={tot} rho={rho:.5f} Gmax={info['Gmax']} naive predicted max g (q^n (1-rho)^g = 1): {math.log(tot) / -math.log(1 - rho):.1f}")
    for k in range(1, 9):
        g = next((g for g in gs if A[g] <= tot * 10 ** -k), None)
        if g is not None: print(f"  A_g <= 10^-{k} q^n from g = {g}: A_g = {A[g]}, naive first moment {tot * (1 - rho) ** g:.3g}")
