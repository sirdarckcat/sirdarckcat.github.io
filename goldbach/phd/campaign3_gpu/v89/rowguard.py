# The lead's guard for f = 0.985 in vector mode (23 Nov 12:01Z): the average row count of the vectors this card's campaign consumed, the last 2,000 of them
# against the average at the switch (/content/rowguard_base.txt, written on the first run: every vector consumed before the switch). If the trailing average
# exceeds the base by more than 2 rows, the card drops to f = 0.98 (SKIPF in /content/next_campaign_env, restart in place) once and writes
# /content/rowguard_tripped.txt. Row counts come from the chunk files (cached per chunk in /content/rowidx). Prints one status line.
import json, os, subprocess, sys, time
IDX = "/content/rowidx"; os.makedirs(IDX, exist_ok=True)
cache = {}
def rows(name):                                       # q170000_m89_p0c00020_v5 -> its residual length, from /content/vec89/vec_000020.json
    c = int(name.split("_")[2].split("c")[1])
    if c not in cache:
        p = f"{IDX}/{c:06d}.json"
        if not os.path.exists(p):
            s = json.load(open(f"/content/vec89/vec_{c:06d}.json"))
            json.dump({x["name"]: len(x["residual"]) if isinstance(x["residual"], list) else len(json.loads(x["residual"])) for x in s}, open(p, "w"))
        cache[c] = json.load(open(p))
    return cache[c][name]
names = [l[1:l.index("@")] for l in open("/content/c170v/search.log") if l.startswith("[q170000_m89")]
r = [rows(n) for n in names]
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
if not os.path.exists("/content/rowguard_base.txt"):
    open("/content/rowguard_base.txt", "w").write(f"{sum(r) / len(r):.4f} {len(r)} {now}\n")
base, nbase = open("/content/rowguard_base.txt").read().split()[:2]
base = float(base); tail = r[-2000:]; ta = sum(tail) / len(tail)
skipf = [e for e in open("/content/next_campaign_env").read().split() if e.startswith("SKIPF=")]
trip = ta > base + 2 and not os.path.exists("/content/rowguard_tripped.txt") and "SKIPF=0.985" in skipf
print(f"[rg] {now} consumed {len(r)} | base {base:.3f} ({nbase} vectors) | last 2000 {ta:.3f} (+{ta - base:.3f}) | all {sum(r) / len(r):.3f} | {skipf} | trip {trip}", flush=True)
if trip and "--dry" not in sys.argv:
    env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("SKIPF=")] + ["SKIPF=0.98"]
    open("/content/next_campaign_env", "w").write(" ".join(env))
    os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
    for _ in range(60):
        if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
            break
        time.sleep(1)
    subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                     shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open("/content/rowguard_tripped.txt", "w").write(f"{now} trailing {ta:.3f} > base {base:.3f} + 2: SKIPF 0.985 -> 0.98, campaign restarted\n")
    print(f"[rg] TRIPPED: SKIPF 0.985 -> 0.98, campaign restarted", flush=True)
