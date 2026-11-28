# Top-of-range windows in vector mode on this RTX card (the lead's decision of 23 Nov 16:36Z, after vtop.sh / vtop2.sh and the CPU brute force at the top):
# /content/c3g/search_gpu5.py becomes the patched driver (search_gpu5_vtop.patch; the old one kept as search_gpu5_pre_vtop.py) and --vector-place top goes into
# /content/deep_env_v89 (old one kept as deep_env_v89_pre_vtop), so every restart path (restart_v.sh, rowguard.py) keeps it. At the next batch end (a vector boundary:
# a new line in gpu3_stats.log) the vector campaign restarts in place: c170v's done set carries over, vectors scanned at the bottom are not taken again (base-name
# exclusion), new vectors get the window [kend - 2^24, kend). Revert: copy the two _pre_vtop files back and restart (restart_v.sh).
import hashlib, os, shutil, subprocess, time
G = "/content/c3g"; C = "/content/c170v"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
cur, new = sha(f"{G}/search_gpu5.py"), sha(f"{G}/search_gpu5_vtop.py")
if new != "f4a85df2f2d5" or cur not in ("13e19e57aa0f", "f4a85df2f2d5"):
    raise SystemExit(f"[dv] unexpected drivers: search_gpu5.py {cur}, search_gpu5_vtop.py {new}; nothing changed")
if cur == "13e19e57aa0f":
    shutil.copy2(f"{G}/search_gpu5.py", f"{G}/search_gpu5_pre_vtop.py")
de = open("/content/deep_env_v89").read().split()
if "--vector-place" not in de:
    shutil.copy2("/content/deep_env_v89", "/content/deep_env_v89_pre_vtop")
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(400):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
shutil.copy2(f"{G}/search_gpu5_vtop.py", f"{G}/.search_gpu5.tmp"); os.replace(f"{G}/.search_gpu5.tmp", f"{G}/search_gpu5.py")
if "--vector-place" not in de:
    open("/content/deep_env_v89", "w").write(" ".join(de + ["--vector-place", "top"]))
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(60):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dv] the old campaign did not exit; nothing started (driver and deep_env_v89 already switched: start it with restart_v.sh)")
subprocess.Popen(f'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh {C} /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if not os.popen("pgrep -f 'bash /content/rowguard[.]sh'").read().strip() and not os.path.exists("/content/rowguard_tripped.txt"):
    subprocess.Popen("nohup bash /content/rowguard.sh > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(40)
sl = [l.split()[0] for l in open(C + "/search.log").read().splitlines()[-8:] if l.startswith("[")]
print("[dv]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(), "| driver", sha(f"{G}/search_gpu5.py"),
      "| deep_env_v89 ...", open("/content/deep_env_v89").read().strip()[-40:], "| guard", os.popen("pgrep -fc 'bash /content/rowguard[.]sh'").read().strip(), "| last slices", sl[-4:])
