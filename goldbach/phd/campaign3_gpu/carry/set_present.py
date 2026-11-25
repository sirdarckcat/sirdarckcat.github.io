# After the carry-over A/B failed (25 Nov 21:02Z; the lead's rule: keep the present path): the present path with the lead's calibration (18:52Z) on this RTX card:
# engine search_gpu5.py = 2377c5775be7 (9385f3b + uarch's insertion-only carry patch + --record) at --carry-over 0, i.e. every deployed code path; fround.py = 88f67789996f (identical
# at carry-over 0); DEEP_ARGS (deep_env_v89) without --carry-over, with --record 160357; NEAR_MISS=140000. Restart in place at a batch end (generator and row guard untouched).
import hashlib, os, re, shutil, subprocess, time
H = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
E, F = "/content/cgate/search_gpu5_carry.py", "/content/cgate/fround_carry.py"
assert H(E) == "2377c5775be7" and H(F) == "88f67789996f", (H(E), H(F))
for src, bak in (("/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_pre_carry.py"), ("/content/f29fr/fround.py", "/content/f29fr/fround_pre_carry.py")):
    if not os.path.exists(bak):
        shutil.copy2(src, bak)
de = open("/content/deep_env_v89").read().strip()
de = re.sub(r"\s*--carry-over \d+", "", de)
if "--record" not in de:
    de += " --record 160357"
open("/content/deep_env_v89.tmp", "w").write(de + "\n"); os.replace("/content/deep_env_v89.tmp", "/content/deep_env_v89")
ne = open("/content/next_campaign_env").read()
ne = re.sub(r"NEAR_MISS=\d+", "NEAR_MISS=140000", ne)
open("/content/next_campaign_env.tmp", "w").write(ne); os.replace("/content/next_campaign_env.tmp", "/content/next_campaign_env")
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
    raise SystemExit("[sp] the old campaign did not exit")
if H("/content/c3g/search_gpu5.py") != "2377c5775be7":
    shutil.copy2(E, "/content/c3g/search_gpu5.py.tmp"); os.replace("/content/c3g/search_gpu5.py.tmp", "/content/c3g/search_gpu5.py")
if H("/content/f29fr/fround.py") != "88f67789996f":
    shutil.copy2(F, "/content/f29fr/fround.py.tmp"); os.replace("/content/f29fr/fround.py.tmp", "/content/f29fr/fround.py")
subprocess.Popen(cmd + " > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(60)
new = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
fl = [json for json in open(C + "/found.jsonl").read().splitlines() if json.strip()] if os.path.exists(C + "/found.jsonl") else []
print("[sp]", "stopped", t_stop, "| restarted", time.strftime("%H:%M:%SZ", time.gmtime()), "| engine", H("/content/c3g/search_gpu5.py"), "fround", H("/content/f29fr/fround.py"),
      "| flags", re.findall(r"--(carry-over \d+|record \d+|near-miss \d+|skip-frac [\d.]+)", new), "| procs", len(new.splitlines()), "| found.jsonl lines", len(fl),
      "| stats", [l[:170] for l in open(st).read().splitlines()[-1:]], "| gen", os.popen("pgrep -fc 'bash /content/vecgen491[.]sh'").read().strip(),
      "| rg", os.popen("pgrep -fc 'bash /content/rowguard491[.]sh'").read().strip())
