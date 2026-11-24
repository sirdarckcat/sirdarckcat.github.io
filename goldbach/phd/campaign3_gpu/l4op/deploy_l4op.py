# The RTX sieve options + uarch's one-pass kernel on this L4, after the gate (opl4gate.sh on gold-l4b: slice lines identical, a 2^25 window at f = 0 per-member identical with the
# known case's 40 inside, >= 1% of a batch). /content/next_campaign_env gets SIEVE200=/content/ua_v10/goldbach/sieve200 and the options below; /content/deep_env gets the
# parameters (the old files kept once as *_pre_l4op). /content/ua_v10 = this card's uaB + f1b904a's sieve200/cuda + fc12768's gbig.py (built here if missing). Restart in place at a
# batch end (the done set carries over). With it the lead's item 8 (18:41Z): KLO = 2^32 - 16 * 2^25 = 3,758,096,384 (the top 16 levels of 2^25 of every vector, then fresh vectors), and
# /content/m88f_top3.json, if present, appended to the campaign's vector list (names checked distinct). The done levels stay in the campaign's search.log (name@k0 a slice).
# OPTIONS=0 below (set by the launcher) applies only KLO and the append (for a card whose own options gate has not passed).
import json
OPTIONS = 1
KLO_TOP16 = (1 << 32) - 16 * (1 << 25)
import os, shutil, subprocess, time
ENV_ADD = "DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256 DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=75".split()
ARGS_ADD = "--deep-rg 32 --deep-gen-threads 512 --deep-tile-threads 512".split()
E, DE = "/content/next_campaign_env", "/content/deep_env"
C = open("/content/next_campaign_dir").read().split()[0]
if not os.path.isdir("/content/ua_v10"):
    os.system("cp -a /content/uaB /content/ua_v10")
os.system("tar -xzf /content/ua10_cuda.tgz -C /content/ua_v10/goldbach/sieve200/cuda")
assert os.path.exists("/content/ua_v10/goldbach/sieve200/cuda/bench_split.py") and "onepass_overflow" in open("/content/ua_v10/goldbach/sieve200/cuda/gbig.py").read()
for f in (E, DE):
    if not os.path.exists(f + "_pre_l4op"):
        shutil.copy2(f, f + "_pre_l4op")
if OPTIONS:
    keys = {e.split("=")[0] for e in ENV_ADD} | {"SIEVE200", "KLO"}
    env = [e for e in open(E + "_pre_l4op").read().split() if e.split("=")[0] not in keys] + ["SIEVE200=/content/ua_v10/goldbach/sieve200"] + ENV_ADD + [f"KLO={KLO_TOP16}"]
    de = open(DE + "_pre_l4op").read().split()
    for i in range(0, len(ARGS_ADD), 2):
        if ARGS_ADD[i] in de:
            j = de.index(ARGS_ADD[i]); de[j + 1] = ARGS_ADD[i + 1]
        else:
            de += ARGS_ADD[i:i + 2]
else:
    env = [e for e in open(E + "_pre_l4op").read().split() if not e.startswith("KLO=")] + [f"KLO={KLO_TOP16}"]
    de = open(DE + "_pre_l4op").read().split()
specs = json.load(open(C + "/my_specs.json"))
if os.path.exists("/content/m88f_top3.json"):
    have = {v["name"] for v in specs}
    add = [v for v in json.load(open("/content/m88f_top3.json")) if v["name"] not in have]
    assert len({v["name"] for v in add}) == len(add)
    specs = specs + add
    if not os.path.exists(C + "/my_specs_pre_top3.json"):
        shutil.copy2(C + "/my_specs.json", C + "/my_specs_pre_top3.json")
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
    raise SystemExit("[dl4] the old campaign did not exit; nothing changed")
open(E, "w").write(" ".join(env)); open(DE, "w").write(" ".join(de))
json.dump(specs, open(C + "/my_specs.json.tmp", "w")); os.replace(C + "/my_specs.json.tmp", C + "/my_specs.json")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {C} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(45)
err = [l[:160] for l in open(C + "/driver.log").read().splitlines()[-40:] if "rror" in l or "Traceback" in l or "refuse" in l]
print("[dl4]", time.strftime("%H:%M:%SZ", time.gmtime()), "| options", OPTIONS, "| vectors", len(specs), "|", [e for e in env if e.startswith(("KLO=", "SIEVE200=", "DEEP_GEN_ONEPASS"))], "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(), "| deep_env", " ".join(de)[-120:],
      "| stats", [l[:140] for l in open(st).read().splitlines()[-2:]], "| errors", err[-2:])
