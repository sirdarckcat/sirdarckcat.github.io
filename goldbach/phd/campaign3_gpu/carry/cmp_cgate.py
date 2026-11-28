import json, os, re
W = "/content/cgate"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (.*)$")
def slices(d):
    out = {}
    for l in open(os.path.join(d, "search.log")):
        m = pat.match(l.rstrip("\n"))
        if m:
            out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return out
def found(d, files=("found.jsonl",)):
    s = set(); rows = []
    for f in files:
        p = os.path.join(d, f)
        if os.path.exists(p):
            for l in open(p):
                if l.strip():
                    r = json.loads(l); rows.append((f, r)); s.add((r.get("name"), int(r["k"]), int(r["g"]), r["N"]))
    return s, rows
def prof(d):
    L = [l for l in open(os.path.join(d, "driver.log")) if l.startswith("[profile-pool] [fused rounds]")]
    rx = re.compile(r"(\d+) members, (\d+) rounds, (\d+) tests: Fermat kernels ([\d.]+) s on the GPU, run_pool wall ([\d.]+) s, gap ([\d.]+) s")
    v = [tuple(float(x) for x in rx.search(l).groups()) for l in L if rx.search(l)]
    use = v[2:] if len(v) > 4 else v
    if not use:
        return f"{len(L)} profile lines, none parsed"
    n = len(use); S = lambda i: sum(x[i] for x in use) / n
    return f"{len(v)} half-pool lines ({n} after warm-up): members {S(0):,.0f}, rounds {S(1):.1f}, tests computed {S(2):,.0f}, kernels {S(3):.3f} s, wall {S(4):.3f} s, gap {S(5):.3f} s a half-pool"
A, B = slices(W + "/runA"), slices(W + "/runB")
same_names = set(A) == set(B)
diff = [n for n in A if n in B and A[n] != B[n]]
print(f"CGATE slices: A {len(A)}, B {len(B)}, same names {same_names}, lines differing {len(diff)} {diff[:3]}")
fa, ra = found(W + "/runA"); fb, rb = found(W + "/runB", ("found.jsonl", "near_events.jsonl"))
bf = [r for f, r in rb if f == "found.jsonl"]; bn = [r for f, r in rb if f == "near_events.jsonl"]
split_ok = all(int(r["g"]) > 160357 for r in bf) and all(r.get("sub_record") is True and int(r["g"]) <= 160357 for r in bn)
print(f"CGATE found: A {len(fa)} events (g {min((x[2] for x in fa), default=0)}..{max((x[2] for x in fa), default=0)}), B {len(fb)} ({len(bf)} in found.jsonl, {len(bn)} in near_events.jsonl), same set {fa == fb}, split correct {split_ok}, duplicates in B {len(rb) - len(fb)}")
ta = sum(int(re.search(r"tests=(\d+)", v[2]).group(1)) for v in A.values()); tb = sum(int(re.search(r"tests=(\d+)", v[2]).group(1)) for v in B.values())
print(f"CGATE tests counted: A {ta:,}, B {tb:,}, equal {ta == tb}")
print("CGATE profile A:", prof(W + "/runA")); print("CGATE profile B:", prof(W + "/runB"))
for d in ("runA", "runB"):
    st = [l for l in open(f"{W}/{d}/gpu3_stats.log")] if os.path.exists(f"{W}/{d}/gpu3_stats.log") else []
    tc = sum(int(re.search(r"tests (\d+) counted, (\d+) computed", l).group(2)) for l in st if re.search(r"tests (\d+) counted", l))
    print(f"CGATE {d}: {len(st)} batch lines, tests computed {tc:,}")
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
fc, _ = found(W + "/runC"); kc = sorted((x[1], x[2]) for x in fc)
print(f"CGATE known case (carry-over engine): {len(kc)} near-misses, identical to the CPU brute force's 23: {kc == REF}")
ok = same_names and not diff and fa == fb and split_ok and ta == tb and kc == REF and len(A) == 28
print("CGATE", "PASSED" if ok else "FAILED")
