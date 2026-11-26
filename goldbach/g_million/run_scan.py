# T5 driver, resumable: after sieve pass 1 (counts), choose the members with the fewest survivors, run pass 2 for their survivor
# rows, then test them in increasing order of survivors until the first hit.
#   python3 run_scan.py tag X B K ncand
import os, sys, subprocess, json
import numpy as np
tag, X, B, K, ncand = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
counts, cand, surv = f"run/counts_{tag}.u16", f"run/cand_{tag}.txt", f"surv_{tag}.txt"
c = np.fromfile(counts, dtype=np.uint16)
assert len(c) == K, (len(c), K)
mu, sd = float(c.mean()), float(c.std())
if not os.path.exists(cand):
    idx = np.argsort(c, kind="stable")[:ncand]
    open(cand, "w").write("\n".join(str(int(k)) for k in sorted(idx)) + "\n")
    thr = int(c[idx[-1]])
    json.dump(dict(K=K, B=B, mean=mu, sd=sd, min=int(c.min()), ncand=ncand, threshold=thr, threshold_sd=(mu - thr) / sd,
                   hist={int(v): int(n) for v, n in zip(*np.unique(c[c <= thr], return_counts=True))}), open(f"selection_{tag}.json", "w"), indent=1)
    print(f"survivors: mean {mu:.2f}, sd {sd:.2f}, min {int(c.min())}; {ncand} candidates with S <= {thr} ({(mu - thr) / sd:.2f} sd below the mean)", flush=True)
if not os.path.exists(surv):
    subprocess.run(["./sieve", f"setup_{tag}.bin", str(X), str(B), str(K), counts, cand, surv + ".part"], env=dict(os.environ, OMP_NUM_THREADS="4"), check=True)
    os.rename(surv + ".part", surv)
tester = os.environ.get("T5_TESTER", "test_members.py")          # test_members_fmw.py: the IFMA kernel
subprocess.run([sys.executable, tester, tag, surv, "4", "--stop-at-hit"], check=True)
