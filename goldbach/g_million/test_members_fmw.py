# T5 step 4 with the uarch session's AVX-512 IFMA kernel (goldbach/fermatw on branch ccr-b8c25887-i6tn9f, commit 63f0b8d, copied to
# run/fermatw): the same tests as test_members.py. Each member's survivors are tested with base-2 Fermat in the order that
# random.Random(k).shuffle gives, until the first probable prime, with 8 numbers in flight per core. Checked against gmpy2 on 48
# members of the 1,997-digit scan (run/validate_fmw.py): the first probable prime was at the same position for all 48, over 5,213 tests.
# A member whose survivors all fail is tested again with gmpy2 before it is reported as a hit.
#   python3 test_members_fmw.py tag survivors.txt [procs] [--stop-at-hit] [--chunk n]
import sys, os, json, time, random
from multiprocessing import Pool
import numpy as np
from gmpy2 import mpz, powmod
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "run", "fermatw"))
import fmw

def init(n0, d, U, kmax):
    global MEM, N0, D, IDX
    MEM = fmw.Members(int(n0), int(d), np.array(U, dtype=np.uint32), kmax)
    N0, D = mpz(n0), mpz(d); IDX = {q: i for i, q in enumerate(U)}

def run_chunk(chunk):
    ks, rows, offs, orders = [], [], [0], []
    for k, surv in chunk:
        order = list(surv); random.Random(k).shuffle(order)
        ks.append(k); orders.append(order); rows += [IDX[q] for q in order]; offs.append(len(rows))
    t0 = time.time(); pos = MEM.first_pass(ks, rows, offs); dt = time.time() - t0
    ntests = sum(int(p) + 1 if p >= 0 else len(o) for p, o in zip(pos, orders))
    out = []
    for k, p, order in zip(ks, pos, orders):
        p = int(p)
        if p >= 0:
            out.append(dict(k=k, S=len(order), dead_at=order[p], tests=p + 1, seconds=round(dt * (p + 1) / ntests, 3), kernel="fmw"))
            continue
        N = N0 + k * D                                            # every survivor failed: check with gmpy2 before reporting
        prp = [q for q in order if powmod(2, N - q - 1, N - q) == 1]
        if prp:
            out.append(dict(k=k, S=len(order), dead_at=prp[0], tests=len(order), kernel="fmw", kernel_error=True, gmpy2_prp=prp[:5]))
        else:
            out.append(dict(k=k, S=len(order), hit=True, tests=len(order), seconds=round(dt * len(order) / ntests, 3), kernel="fmw",
                            gmpy2_checked=True))
    return out

if __name__ == "__main__":
    tag, survf = sys.argv[1], sys.argv[2]
    procs = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 4
    stop_at_hit = "--stop-at-hit" in sys.argv
    chunk = int(sys.argv[sys.argv.index("--chunk") + 1]) if "--chunk" in sys.argv else 32
    setup = json.load(open(f"setup_{tag}.json")); U = [int(q) for q in setup["rows_left"]]
    log = f"tested_{tag}.jsonl"; done = set()
    if os.path.exists(log):
        for l in open(log):
            try: done.add(json.loads(l)["k"])
            except Exception: pass
    jobs = []
    for line in open(survf):
        t = line.split(); k = int(t[0])
        if k not in done: jobs.append((k, [int(v) for v in t[2:]]))
    jobs.sort(key=lambda j: len(j[1]))
    chunks = [jobs[i:i + chunk] for i in range(0, len(jobs), chunk)]
    kmax = max([k for k, _ in jobs] + [0]) + 1                    # the kernel's limb count is set by the largest member tested
    L = fmw.limbs_for((int(setup["N0"]) + kmax * int(setup["D"])).bit_length())
    print(f"{len(jobs)} members to test ({len(done)} already done), {len(chunks)} chunks of {chunk}, fmw kernel L = {L}", flush=True)
    fmw.lib(L)                                                    # compile once, before the workers
    t0 = time.time(); n = 0; nt = 0; hit = None
    with Pool(procs, initializer=init, initargs=(setup["N0"], setup["D"], U, kmax)) as pool, open(log, "a") as f:
        for res in pool.imap(run_chunk, chunks):
            for r in res:
                f.write(json.dumps(r) + "\n"); n += 1; nt += r["tests"]
                if r.get("kernel_error"): print(f"KERNEL ERROR at k = {r['k']}: gmpy2 finds PRP rows {r['gmpy2_prp']}", flush=True)
                if r.get("hit") and hit is None:
                    hit = r
                    print(f"HIT: k = {r['k']} with {r['S']} survivors, all composite (fmw, checked with gmpy2) ({time.time() - t0:.0f} s)", flush=True)
                    open(f"hit_{tag}_k{r['k']}.json", "w").write(json.dumps(dict(k=r["k"], N=str(mpz(setup["N0"]) + r["k"] * mpz(setup["D"])))) + "\n")
            f.flush()
            if hit is not None and stop_at_hit: pool.terminate(); break
            if (n // chunk) % 10 == 0: print(f"  {n} tested, {nt} tests ({time.time() - t0:.0f} s; {1000 * (time.time() - t0) * procs / max(nt, 1):.1f} ms a test per core)", flush=True)
    print(f"done: {n} members tested in {time.time() - t0:.0f} s")
