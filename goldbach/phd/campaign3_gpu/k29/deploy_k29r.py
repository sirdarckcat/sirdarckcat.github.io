# 29-bit Fermat kernel (uarch 710585f: 23 x 29-bit limbs, R = 2^669, n < 2^665) on this RTX card, under the lead's standing rule for engine changes. Deploys only if
# /content/k29v/result.txt (k29v.sh on this card) shows the slice lines of its 24 test windows IDENTICAL for v0, k29 and v0b with no range errors, and the
# known case's 23 members (k, q) exactly as the CPU brute force found them. Driver search_gpu5_k29.py (the v89 driver + the kernel's own n-range) as
# search_gpu5.py (the old one kept as search_gpu5_prev4.py), FERMAT28_DIR=/content/f29, K28_STEP=fermat29_step_s1.cuh (asm 1). Restart in place: the
# search.log done-set of /content/c170v carries over; the vector producer (vecgen.sh) keeps running.
import os, re, subprocess, time, shutil, hashlib
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
R = open("/content/k29v/result.txt").read() if os.path.exists("/content/k29v/result.txt") else ""
got = sorted((int(a), int(b)) for a, b in re.findall(r"^K29 k=(\d+) q=(\d+)$", R, re.M))
ident = len(re.findall(r"slice lines vs v0: IDENTICAL \(24\)", R))
bad = [l for l in R.splitlines() if "outside" in l or "Traceback" in l or "rror" in l]
if not ("K29V-DONE" in R and ident == 3 and not bad and got == REF):
    raise SystemExit(f"[dk] gate NOT passed (done {'K29V-DONE' in R}, identical {ident}/3, bad {bad[:2]}, known case {len(got)} members, equal {got == REF}): nothing changed")
cur, new, prev = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_k29.py", "/content/c3g/search_gpu5_prev4.py"
assert os.path.exists("/content/f29/fermat29_step_s1.cuh") and os.path.exists("/content/f29/gpu_fermat28.py")
if not os.path.exists(prev):
    shutil.copy2(cur, prev)
shutil.copy2(new, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("FERMAT28_DIR=", "K28_STEP=", "K28_ASM="))]
env += ["FERMAT28_DIR=/content/f29", "K28_STEP=fermat29_step_s1.cuh", "K28_ASM=1"]
open("/content/next_campaign_env", "w").write(" ".join(env))
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dk] the old campaign did not exit; nothing started (driver and env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[dk]", time.strftime("%H:%M:%SZ", time.gmtime()), "| driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "| procs",
      os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", [e for e in env if e.startswith(("FERMAT28_DIR=", "K28_STEP=", "K28_ASM="))])
