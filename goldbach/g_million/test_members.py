# T5 step 4: test the selected members. For each member (fewest survivors first) the rows that survived the sieve are tested with
# a base-2 Fermat test on N - q; the first probable prime kills the member. A member whose survivors all fail is a hit: every
# N - q for q < Q is then composite (divisible by a modulus, by a sieve prime, or a Fermat witness), so g(N) >= Q.
# Resumable: every member tested is appended to tested_<tag>.jsonl.
#   python3 test_members.py tag survivors_<tag>.txt [procs]
import sys, os, json, time, random
from multiprocessing import Pool
import gmpy2
from gmpy2 import mpz, powmod

def init(n0, d):
    global N0, D
    N0, D = mpz(n0), mpz(d)

def test_member(job):
    k, rows = job
    N = N0 + k * D
    order = list(rows); random.Random(k).shuffle(order)
    t0 = time.time()
    for i, q in enumerate(order):
        m = N - q
        if powmod(2, m - 1, m) == 1:
            return dict(k=k, S=len(rows), dead_at=q, tests=i + 1, seconds=round(time.time() - t0, 2))
    return dict(k=k, S=len(rows), hit=True, tests=len(order), seconds=round(time.time() - t0, 2))

if __name__ == "__main__":
    tag, survf = sys.argv[1], sys.argv[2]; procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    stop_at_hit = "--stop-at-hit" in sys.argv
    setup = json.load(open(f"setup_{tag}.json"))
    done = set()
    log = f"tested_{tag}.jsonl"
    if os.path.exists(log):
        for l in open(log):
            try: done.add(json.loads(l)["k"])
            except Exception: pass
    jobs = []
    for line in open(survf):
        t = line.split(); k = int(t[0])
        if k not in done: jobs.append((k, [int(v) for v in t[2:]]))
    jobs.sort(key=lambda j: len(j[1]))
    print(f"{len(jobs)} members to test ({len(done)} already done)", flush=True)
    t0 = time.time(); n = 0
    with Pool(procs, initializer=init, initargs=(setup["N0"], setup["D"])) as pool, open(log, "a") as f:
        for r in pool.imap_unordered(test_member, jobs, chunksize=1):
            f.write(json.dumps(r) + "\n"); f.flush(); n += 1
            if r.get("hit"):
                print(f"HIT: k = {r['k']} with {r['S']} survivors, all composite ({time.time() - t0:.0f} s)", flush=True)
                open(f"hit_{tag}_k{r['k']}.json", "w").write(json.dumps(dict(k=r["k"], N=str(mpz(setup["N0"]) + r["k"] * mpz(setup["D"])))) + "\n")
                if stop_at_hit: break
            if n % 200 == 0: print(f"  {n} tested ({time.time() - t0:.0f} s)", flush=True)
    print(f"done: {n} members tested in {time.time() - t0:.0f} s")
