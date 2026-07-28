"""Fleet driver for the GPU desert campaign (HARVEST FIRST protocol).

Encodes the supervision loop that previously lived in check-in prompts:
harvest each shard's scan log, advance the committed resume mark
(safe_k), rescue any CANDIDATE lines into git before anything else can
lose them, and relaunch sessions that Colab has culled.

The state file (campaign_state.json) is authoritative and lives in git;
safe_k only advances past log ranges actually read with no CANDIDATE,
so a dead session can never lose a hit -- only cost rescan time.

Commands:
  fleet.py cycle            full harvest/advance/relaunch pass
  fleet.py status           read-only probe of all shards
  fleet.py relaunch SHARD   force-relaunch one shard from its safe_k

Exit codes: 0 ok, 2 CANDIDATE rescued (verify + package next), 3 all
shards complete, 4 attention needed (crash / launch failure / timeout).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GPU_DIR = Path(__file__).resolve().parent
REPO = GPU_DIR.parent.parent
STATE = GPU_DIR / "campaign_state.json"
HITS = GPU_DIR / "hits_incoming.jsonl"
TILE = 2097152                      # engine default --tile
CACHE = Path(os.environ.get("FLEET_CACHE",
                            Path.home() / ".cache" / "goldbach-fleet"))
TRAILER = os.environ.get(
    "FLEET_COMMIT_TRAILER",
    "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n"
    "Claude-Session: https://claude.ai/code/session_01ShDozEmrVVu7nEEUgsVnRS")

RE_TILE = re.compile(r"tile k0=(\d+):")
RE_CAND = re.compile(r"CANDIDATE k=(\d+)")
RE_DONE = re.compile(r"DONE k=\[(\d+),(\d+)\)")

TAIL_SCRIPT = """\
import os
log = open("/content/scan.log").read() if os.path.exists("/content/scan.log") else ""
for l in log.splitlines():
    if "CANDIDATE" in l or "DONE" in l:
        print(l)
print("--TAIL--")
print(log[-500:])
"""

HITS_SCRIPT = """\
import os
p = "/content/hits.jsonl"
print(open(p).read() if os.path.exists(p) else "")
"""

PGREP_SCRIPT = """\
import subprocess
r = subprocess.run("pgrep -af "engine" || true", shell=True,
                   capture_output=True, text=True)
print(r.stdout.strip())
"""


def sh(cmd, timeout=120):
    env = dict(os.environ)
    env["PATH"] = f"{Path.home()}/.local/bin:" + env.get("PATH", "")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, env=env, cwd=REPO)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "<timeout>"


def temp_script(body):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = tempfile.NamedTemporaryFile("w", dir=CACHE, suffix=".py",
                                    delete=False)
    f.write(body)
    f.close()
    return f.name


def colab_exec(session, body, timeout=90):
    path = temp_script(body)
    rc, out = sh(f"colab exec -s {session} -f {path} --timeout {timeout}",
                 timeout=timeout + 60)
    return rc, out


def bootstrap():
    rc, out = sh(f"bash {GPU_DIR}/bootstrap.sh", timeout=180)
    if rc != 0:
        print(f"bootstrap failed:\n{out}")
    return rc == 0


def load_state():
    return json.loads(STATE.read_text())


def save_state(state):
    state["updated"] = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    STATE.write_text(json.dumps(state, indent=1))


def probe(shard):
    """Read a shard's scan log. Returns dict with status in
    {reading, lost, timeout, empty}, plus last_k0/candidates/done."""
    rc, out = colab_exec(shard, TAIL_SCRIPT)
    if rc == -1 or "<timeout>" in out:
        return {"status": "timeout", "raw": out}
    if "appears to be lost" in out or "No active sessions" in out:
        return {"status": "lost", "raw": out}
    tiles = RE_TILE.findall(out)
    cands = sorted(set(int(k) for k in RE_CAND.findall(out)))
    done = RE_DONE.search(out)
    if not tiles and not done and "--TAIL--" not in out:
        # exec ran but output is not our script's (CLI error etc.)
        return {"status": "lost", "raw": out}
    return {"status": "reading" if (tiles or done) else "empty",
            "last_k0": int(tiles[-1]) if tiles else None,
            "candidates": cands, "done": bool(done), "raw": out}


def rescue_hits(shard):
    """Pull hits.jsonl off the session and append new lines locally."""
    rc, out = colab_exec(shard, HITS_SCRIPT)
    lines = [l for l in out.splitlines() if l.strip().startswith("{")]
    if not lines:
        return 0
    seen = set()
    if HITS.exists():
        seen = {l.strip() for l in HITS.read_text().splitlines()}
    new = [l.strip() for l in lines if l.strip() not in seen]
    if new:
        with HITS.open("a") as f:
            for l in new:
                f.write(l + "\n")
    return len(new)


def git_push(msg):
    CACHE.mkdir(parents=True, exist_ok=True)
    mf = CACHE / "commit_msg.txt"
    mf.write_text(msg + "\n\n" + TRAILER + "\n")
    rc, out = sh("git add goldbach/gpu/campaign_state.json; "
                 "git add goldbach/gpu/hits_incoming.jsonl 2>/dev/null; "
                 "git diff --cached --quiet && echo NOCHANGE || "
                 f"git commit -q -F {mf}")
    if "NOCHANGE" in out:
        return True
    if rc != 0:
        print(f"commit failed:\n{out}")
        return False
    for i, wait in enumerate([0, 2, 4, 8, 16]):
        if wait:
            time.sleep(wait)
        rc, out = sh("git push -q -u origin "
                     "claude/goldbach-crt-optimization-ou17zd", timeout=60)
        if rc == 0:
            return True
    print(f"push failed after retries:\n{out}")
    return False


def relaunch(shard, cfg):
    """Fresh session + upload + detached launch from safe_k."""
    engine = GPU_DIR / cfg.get("engine", "engine150.py")
    spec = GPU_DIR / cfg.get("spec", "spec150.json")
    k0, kend = cfg["safe_k"], cfg["range"][1]
    if k0 >= kend:
        cfg["complete"] = True
        return "complete"
    gpus = [cfg.get("gpu", "T4")]
    if gpus[0] != "T4":
        gpus.append("T4")            # fallback when A100 pool is dry
    up = None
    for gpu in gpus:
        rc, out = sh(f"colab new -s {shard} --gpu {gpu}", timeout=300)
        if "READY" in out:
            up = gpu
            break
        print(f"[{shard}] colab new --gpu {gpu} failed: {out.strip()[-200:]}")
    if not up:
        return "launch-failed"
    for local, remote in [(engine, "/content/engine.py"),
                          (spec, "/content/spec.json")]:
        ok = False
        for _ in range(2):
            rc, out = sh(f"colab upload -s {shard} {local} {remote}",
                         timeout=180)
            if "Uploaded" in out:
                ok = True
                break
        if not ok:
            print(f"[{shard}] upload {local} failed: {out.strip()[-200:]}")
            return "launch-failed"
    launcher = (
        "import subprocess\n"
        "subprocess.Popen(\"nohup python /content/engine.py "
        f"/content/spec.json {k0} {kend} --out /content/hits.jsonl "
        "> /content/scan.log 2>&1 &\", shell=True)\n"
        "print('launched')\n")
    colab_exec(shard, launcher, timeout=30)
    rc, out = colab_exec(shard, PGREP_SCRIPT, timeout=30)
    if "/content/engine" not in out:
        rc, out = colab_exec(shard, TAIL_SCRIPT)
        print(f"[{shard}] engine not running after launch; log tail:\n"
              f"{out[-500:]}")
        return "launch-failed"
    return f"relaunched on {up} from k={k0}"


def run_cycle(force_shard=None):
    if not bootstrap():
        return 4
    state = load_state()
    attention = candidate = False
    summaries = []
    for shard, cfg in state["shards"].items():
        if force_shard and shard != force_shard:
            continue
        span = cfg["range"][1] - cfg["range"][0]
        if cfg.get("complete"):
            summaries.append(f"{shard}: complete")
            continue
        if force_shard:
            res = relaunch(shard, cfg)
            summaries.append(f"{shard}: {res} (forced)")
            attention |= res == "launch-failed"
            continue
        p = probe(shard)
        if p["status"] == "timeout":
            summaries.append(f"{shard}: probe timeout, skipped")
            attention = True
            continue
        if p["status"] == "empty":
            rc, out = colab_exec(shard, PGREP_SCRIPT, timeout=30)
            if "/content/engine" in out:
                summaries.append(f"{shard}: alive, warming up")
            else:
                res = relaunch(shard, cfg)
                summaries.append(f"{shard}: engine dead (empty log) -> {res}")
                attention |= res == "launch-failed"
            continue
        if p["status"] == "reading":
            new_cands = [c for c in p["candidates"]
                         if c not in cfg.get("banked", [])]
            if new_cands:
                n = rescue_hits(shard)
                candidate = True
                summaries.append(
                    f"{shard}: CANDIDATE k={new_cands} "
                    f"({n} new rescued)")
                git_push(f"fleet: rescue {len(new_cands)} candidate(s) "
                         f"from {shard}")
                # do not advance safe_k past a candidate: leave the mark
                # below it until verification banks the record
                continue
            if p["done"]:
                cfg["safe_k"] = cfg["range"][1]
                cfg["complete"] = True
                summaries.append(f"{shard}: DONE, shard complete")
            elif p["last_k0"] is not None:
                new_k = min(p["last_k0"] + TILE, cfg["range"][1])
                if new_k > cfg["safe_k"]:
                    cfg["safe_k"] = new_k
                pct = 100 * (cfg["safe_k"] - cfg["range"][0]) / span
                summaries.append(
                    f"{shard}: alive k={cfg['safe_k']:.3e} ({pct:.1f}%)")
            continue
        # lost: relaunch from the committed mark
        res = relaunch(shard, cfg)
        summaries.append(f"{shard}: was lost -> {res}")
        attention |= res == "launch-failed"
    save_state(state)
    marks = ", ".join(f"{n} {c['safe_k']:.2e}"
                      for n, c in state["shards"].items())
    git_push(f"campaign_state: fleet cycle ({marks})")
    print("\n".join(summaries))
    total_span = sum(c["range"][1] - c["range"][0]
                     for c in state["shards"].values())
    total_done = sum(min(c["safe_k"], c["range"][1]) - c["range"][0]
                     for c in state["shards"].values())
    print(f"campaign: {100 * total_done / total_span:.1f}% of round scanned")
    if candidate:
        return 2
    if all(c.get("complete") for c in state["shards"].values()):
        return 3
    return 4 if attention else 0


def run_status():
    if not bootstrap():
        return 4
    state = load_state()
    for shard, cfg in state["shards"].items():
        p = probe(shard)
        tail = p.get("raw", "").split("--TAIL--")[-1].strip()[-300:]
        print(f"=== {shard} ({cfg.get('gpu')}) safe_k={cfg['safe_k']} "
              f"[{p['status']}] ===\n{tail}\n")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"
    if cmd == "cycle":
        sys.exit(run_cycle())
    elif cmd == "status":
        sys.exit(run_status())
    elif cmd == "relaunch":
        sys.exit(run_cycle(force_shard=sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
