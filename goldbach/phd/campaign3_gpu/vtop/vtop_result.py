import json, os, re
W = "/content/vtop"
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def sl(f):
    return {m.group(1): (int(m.group(2)), int(m.group(3)), m.group(4)) for m in map(pat.match, rd(f)) if m}
def errs(f):
    return [l.strip()[:160] for l in rd(f) if "rror" in l or "Traceback" in l or "outside" in l or "ssert" in l][:3]
def nms(d):
    return sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in rd(f"{W}/{d}/camp/found.jsonl") if l.strip()))
print(open(f"{W}/status.txt").read().strip())
print(open(f"{W}/loader.txt").read().strip())
kb = nms("kc_bot"); print(f"kc_bot (patched driver, default placement): {len(kb)} near-misses >= 46171, identical to the CPU brute force's 23: {kb == REF} | {sl(W + '/kc_bot/camp/search.log')} | {errs(W + '/kc_bot/camp/driver.log')}")
kt = nms("kc_top"); print(f"kc_top (--vector-place top): {len(kt)} near-misses >= 46171 | slice {sl(W + '/kc_top/camp/search.log')} | {errs(W + '/kc_top/camp/driver.log')}")
for k, q in kt:
    print(f"GPU k={k} q={q}")
ok_n = True
for f in ("97", "90"):
    g, c = sl(f"{W}/n{f}/search.log"), sl(f"{W}/c{f}/out.txt")
    same = bool(g) and g == c and not errs(f"{W}/n{f}/driver.log"); ok_n = ok_n and same
    print(f"normal path f = 0.{f}: GPU {g} | CPU {c} | {'IDENTICAL' if same else 'DIFFERENT'} | {errs(W + '/n' + f + '/driver.log')} {errs(W + '/c' + f + '/out.txt')}")
def gaps(d):
    v = [tuple(map(float, l.split())) for l in rd(f"{W}/{d}/stamps.txt")]
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
def near(d):
    e = [float(m.group(1)) for m in (re.search(r"expected near>=158209 (\S+),", l) for l in rd(f"{W}/{d}/gpu3_stats.log")) if m]
    h = [float(m.group(1)) for m in (re.search(r"expected hits (\S+),", l) for l in rd(f"{W}/{d}/gpu3_stats.log")) if m]
    return sum(e), sum(h), len(e)
ref = sl(f"{W}/base/search.log"); ok_b = len(ref) == 24; m = {}
for d in ("base", "bot", "top", "base_b", "bot_b", "top_b"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan")
    s = sl(f"{W}/{d}/search.log")
    if d.startswith("bot"):
        same = bool(s) and s == ref and not errs(f"{W}/{d}/driver.log"); ok_b = ok_b and same; cmpx = "IDENTICAL" if same else "DIFFERENT"
    elif d.startswith("top"):
        cmpx = f"{len(s)} slices, kstart {sorted({v[0] for v in s.values()})[:3]}, names {sorted(s)[:1]}"
    else:
        cmpx = "reference"
    en, eh, nb = near(d)
    print(f"{d:6s}: gaps {[round(x, 3) for x in g]} | mean of batches 2-5 {m[d]:.3f} s | slice lines: {cmpx} ({len(s)}) | expected near>=158209 {en:.4e}, hits {eh:.4e} over {nb} batches | {errs(W + '/' + d + '/driver.log')}")
b = (m["base"] + m["base_b"]) / 2; o = (m["bot"] + m["bot_b"]) / 2; t = (m["top"] + m["top_b"]) / 2
nb_, nt_ = near("base")[0] + near("base_b")[0], near("top")[0] + near("top_b")[0]; hb_, ht_ = near("base")[1] + near("base_b")[1], near("top")[1] + near("top_b")[1]
print(f"batch: base {b:.3f} s, bottom (patched) {o:.3f} s (x{o / b:.4f}), top {t:.3f} s (x{t / b:.4f}) | expected near-misses top / bottom x{nt_ / nb_:.4f}, expected hits x{ht_ / hb_:.4f} (the same 24 vectors)")
ld = "LOADER PASSED" in open(f"{W}/loader.txt").read()
print("VTOP-GPU", "PASSED" if ld and kb == REF and ok_n and ok_b else "FAILED", f"(loader {ld}, kc_bot {kb == REF}, normal path {ok_n}, bottom identity {ok_b}; kc_top to compare with the CPU brute force)")
print("VTOP-DONE")
