# The lead's item 1 (carry-over, 25 Nov 17:57Z) and calibration threshold (18:52Z) on this RTX card, after the identity gate (CGATE PASSED 19:51Z):
# engine search_gpu5.py <- the carry-over engine (2377c5775be7), fround.py <- fround_carry.py (88f67789996f), backups kept; DEEP_ARGS (deep_env_v89) + --carry-over 1 --record 160357;
# NEAR_MISS 160357 -> 140000 (sub-record events to near_events.jsonl, records stay in found.jsonl). Restart in place at a batch end with the campaign's own command (done set carries over;
# the generator and the row guard are not touched).
import hashlib, os, re, shutil, subprocess, time
H = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
E, F = "/content/cgate/search_gpu5_carry.py", "/content/cgate/fround_carry.py"
assert H(E) == "2377c5775be7" and H(F) == "88f67789996f", (H(E), H(F))
assert H("/content/c3g/search_gpu5.py") == "4f27d916ea93", H("/content/c3g/search_gpu5.py")
for src, bak in (("/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_pre_carry.py"), ("/content/f29fr/fround.py", "/content/f29fr/fround_pre_carry.py")):
    if not os.path.exists(bak):
        shutil.copy2(src, bak)
de = open("/content/deep_env_v89").read().strip()
if "--carry-over" not in de:
    open("/content/deep_env_v89.tmp", "w").write(de + " --carry-over 1 --record 160357\n"); os.replace("/content/deep_env_v89.tmp", "/content/deep_env_v89")
ne = open("/content/next_campaign_env").read()
if "NEAR_MISS=160357" in ne:
    open("/content/next_campaign_env.tmp", "w").write(ne.replace("NEAR_MISS=160357", "NEAR_MISS=140000")); os.replace("/content/next_campaign_env.tmp", "/content/next_campaign_env")
C = "/content/c170r"
cmd = 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170r /content/vec491'
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(1200):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
t_stop = time.strftime("%H:%M:%SZ", time.gmtime())
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dc] the old campaign did not exit")
shutil.copy2(E, "/content/c3g/search_gpu5.py.tmp"); os.replace("/content/c3g/search_gpu5.py.tmp", "/content/c3g/search_gpu5.py")
shutil.copy2(F, "/content/f29fr/fround.py.tmp"); os.replace("/content/f29fr/fround.py.tmp", "/content/f29fr/fround.py")
subprocess.Popen(cmd + " > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(60)
new = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
print("[dc]", "stopped", t_stop, "| restarted", time.strftime("%H:%M:%SZ", time.gmtime()), "| engine", H("/content/c3g/search_gpu5.py"), "fround", H("/content/f29fr/fround.py"),
      "| flags", re.findall(r"--(carry-over \d+|record \d+|near-miss \d+)", new), "| procs", len(new.splitlines()),
      "| stats", [l[:200] for l in open(st).read().splitlines()[-1:]], "| gen", os.popen("pgrep -fc 'bash /content/vecgen491[.]sh'").read().strip(),
      "| rg", os.popen("pgrep -fc 'bash /content/rowguard491[.]sh'").read().strip(), "| driver tail", open(C + "/driver.log").read().splitlines()[-2:])
