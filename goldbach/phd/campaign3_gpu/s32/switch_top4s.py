# Switch this L4/T4 campaign to its top32-shifted family-B share (/content/top4s.json) at a batch end (the lead's 20:34Z approval; gate s32gate.sh passed).
# The campaign's vector list becomes the shifted share only (the old my_specs.json kept as my_specs_pre_top4s.json); env and deep_env unchanged; the done set
# (search.log) carries over, so nothing done is lost. The shifted names (q170000_m88f_top4s_v*) are checked distinct from everything in the done set.
import json, os, re, shutil, subprocess, time
C = open("/content/next_campaign_dir").read().split()[0]
new = json.load(open("/content/top4s.json"))
assert new and all("_top4s_" in v["name"] and int(v["k_shift"]) > 0 for v in new) and len({v["name"] for v in new}) == len(new)
done = {m.group(1).split("@")[0] for m in (re.match(r"\[(\S+)\] k=\[", l) for l in open(C + "/search.log")) if m}
assert not done & {v["name"] for v in new}, "shifted names already in the done set"
assert all(int(v["N0"]) + ((1 << 32) - 1) * int(v["M"]) < 10 ** 200 and int(v["N0"]) + 3758096384 * int(v["M"]) >= 10 ** 199 for v in new)
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(600):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[s4] the old campaign did not exit; nothing changed")
if not os.path.exists(C + "/my_specs_pre_top4s.json"):
    shutil.copy2(C + "/my_specs.json", C + "/my_specs_pre_top4s.json")
json.dump(new, open(C + "/my_specs.json.tmp", "w")); os.replace(C + "/my_specs.json.tmp", C + "/my_specs.json")
for f in ("/content/m88f_top3.json", "/content/m88f_top2.json"):
    if os.path.exists(f):
        open(f, "w").write("[]")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {C} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(50)
err = [l[:160] for l in open(C + "/driver.log").read().splitlines()[-40:] if "rror" in l or "Traceback" in l or "refuse" in l]
print("[s4]", time.strftime("%H:%M:%SZ", time.gmtime()), "| dir", C, "| vectors", len(new), new[0]["name"], "..", new[-1]["name"], "| procs",
      os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(), "| env", [e for e in open("/content/next_campaign_env").read().split() if e.startswith(("KLO=", "DEEP_GEN_ONEPASS"))],
      "| stats", [l[:150] for l in open(st).read().splitlines()[-2:]], "| last slices", [l[:110] for l in open(C + "/search.log").read().splitlines()[-2:]], "| errors", err[-2:])
