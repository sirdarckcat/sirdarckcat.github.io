# The 25% line of the closeness frontier (the research session's request, 25 November).
# Goal: an N of d digits with g(N) >= 0.25 * ceiling(N), with ceiling from the research session's goldbach/closeness.py (branch
# ccr-d4a17dd0-7uu03r, commit 93d7ec4; copied, with ceiling_table.json, to ../g_million/run/closeness).
#
# The window, as the research session proposed: scan 10^(d-1) <= N <= c 10^(d-1) with the target Q = ceil(0.25 ceiling(c 10^(d-1))).
# The ceiling increases with N, so every hit then has closeness >= 25%. The moduli are the odd primes r taken while
# 2 prod r <= (c - 1) 10^(d-1) / 2^24, so that each cover keeps at least 2^24 members in the window.
#
# The covers are many distinct near-floor class vectors: greedy plus descent (../g_million/cover.py), then 2,000-sweep heat-bath
# anneals with different seeds (../g_million/heatbath2), best first. Each cover gives a spec for the uarch session's
# goldbach/sieve200/search_c.py (branch ccr-b8c25887-i6tn9f, commit 63f0b8d; copied to ../g_million/run/uarch). That engine sieves
# the residual rows, tests the members with the fm13 IFMA kernel, and re-verifies every success with BPSW on all primes below Q.
# The specs run one at a time, and the rung stops at the first success.
#   python3 rung.py d c [--seeds n] [--procs p] [--skip f] [--sieve-b B] [--max-specs m] [--kspan k] [--prepare-only]
import sys, os, json, math, subprocess, time, glob
HERE = os.path.dirname(os.path.abspath(__file__))
GM = os.path.join(HERE, "..", "g_million")
sys.path.insert(0, os.path.join(GM, "run", "closeness"))
import closeness

def opt(name, default, cast=float):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default

def odd_primes(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(3, n + 1) if s[i]]

def crt_even(pairs):
    N, m = 0, 2
    for r, a in pairs:
        t = ((a - N) * pow(m, -1, r)) % r; N += m * t; m *= r
    return N % m, m

if __name__ == "__main__":
    d, c = int(sys.argv[1]), float(sys.argv[2])
    seeds, procs = opt("--seeds", 2000, int), opt("--procs", 2, int)
    skip, sieve_b, max_specs = opt("--skip", 0.92), opt("--sieve-b", 1000000, int), opt("--max-specs", 10 ** 6, int)
    kspan = opt("--kspan", 0, int)
    lo = 10 ** (d - 1); hi = (round(c * 1000) * 10 ** (d - 1)) // 1000
    Q = math.ceil(0.25 * closeness.ceiling(math.log(hi)))
    room = (hi - lo) / 2 ** 24; mods, M = [], 2
    for r in odd_primes(1000):
        if M * r > room: break
        mods.append(r); M *= r
    X = mods[-1]
    tag = f"d{d}_c{c:g}"; wd = os.path.join(HERE, "runs", tag); os.makedirs(wd, exist_ok=True)
    lnN = math.log((lo + hi) / 2); p = 2 * math.prod(r / (r - 1) for r in mods) / lnN
    pp = math.exp(0.5772156649) * math.log(sieve_b) / lnN
    info = dict(d=d, c=c, Q=Q, ceiling_hi=closeness.ceiling(math.log(hi)), moduli=len(mods), X=X, M=str(M), members_per_cover=(hi - lo) // M,
                p=p, p_after_sieve=pp, sieve_b=sieve_b, skip=skip)
    print(json.dumps(info), flush=True)
    json.dump(info, open(os.path.join(wd, "rung.json"), "w"), indent=1)
    # covers
    cov_file = os.path.join(wd, "covers.json")
    if not os.path.exists(cov_file):
        env = dict(os.environ, COVER_Q=str(Q))
        subprocess.run([sys.executable, os.path.join(GM, "cover.py"), str(X), "0"], cwd=wd, env=env, check=True, stdout=subprocess.DEVNULL)
        start = os.path.join(wd, f"cover_X{X}_Q{Q}.txt"); tmp = os.path.join(wd, "hb_tmp.txt"); seen = {}
        t0 = time.time()
        for s in range(1, seeds + 1):
            subprocess.run([os.path.join(GM, "heatbath2"), str(Q), start, "2000", "0.8", "8.0", str(s), tmp], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            l = open(tmp).read().split("\n"); rows = int(l[0].split("rows in no class: ")[1].split()[0])
            seen.setdefault(l[1].strip(), rows)
        covers = sorted(((rows, cls) for cls, rows in seen.items()), key=lambda t: t[0])
        json.dump([dict(rows=r, cover=cls) for r, cls in covers], open(cov_file, "w"))
        hist = {}
        for r, _ in covers: hist[r] = hist.get(r, 0) + 1
        print(f"{len(covers)} distinct covers from {seeds} seeds in {time.time() - t0:.0f} s; rows: {sorted(hist.items())[:10]}", flush=True)
    covers = json.load(open(cov_file))
    # specs
    rowsQ = odd_primes(Q - 1)
    found = os.path.join(wd, "found.jsonl"); done_f = os.path.join(wd, "done.txt")
    done = set(open(done_f).read().split()) if os.path.exists(done_f) else set()
    if "--prepare-only" in sys.argv: sys.exit(0)
    t0 = time.time(); n = 0
    for i, cv in enumerate(covers[:max_specs]):
        name = f"c25_{tag}_cov{i}"
        if name in done: continue
        if os.path.exists(found) and os.path.getsize(found) > 0: break
        pairs = [tuple(map(int, w.split(":"))) for w in cv["cover"].split()]
        N0, MM = crt_even(pairs); assert MM == M
        U = [q for q in rowsQ if all(q % r != a for r, a in pairs)]
        assert len(U) == cv["rows"], (len(U), cv["rows"])
        kstart = -((lo - N0) // -M); kmax = (hi - N0) // M + 1
        if kspan: kmax = min(kmax, kstart + kspan)                      # a short range, for timing
        spec = dict(name=name, N0=str(N0), M=str(M), residual=U, Q=Q, cover=[[r, a] for r, a in pairs], kstart=kstart, kmax=kmax,
                    stop_on_success=True)
        sp = os.path.join(wd, "spec_cur.json"); json.dump(spec, open(sp, "w"))
        r = subprocess.run([sys.executable, os.path.join(GM, "run", "uarch", "goldbach", "sieve200", "search_c.py"), sp, "--procs", str(procs),
                            "--sort-tests", "--skip-frac", str(skip), "--p-est", f"{pp:.4f}", "--sieve-b", str(sieve_b), "--out", found],
                           capture_output=True, text=True)
        line = [l for l in r.stdout.split("\n") if l.startswith("[")]
        print(f"cover {i} (rows {cv['rows']}): {line[-1] if line else r.stdout[-300:] + r.stderr[-300:]} ({time.time() - t0:.0f} s)", flush=True)
        open(done_f, "a").write(name + "\n"); n += 1
    if os.path.exists(found) and os.path.getsize(found) > 0:
        print("FOUND:", open(found).read().strip()[:3000], flush=True)
