# (final version, 26 Nov: + near_events.jsonl and kernel_discrepancy.jsonl of each campaign dir)
# A snapshot of this card's campaign state and trees before its runtime ends (Colab's 24 h limit): /content/snap.tgz, without the regenerable vector chunks (vec89/vec_*.json)
# and caches. Contents: the trees (c3g, ua_*, uaB, f29fr, f28w, cover89 and cover491 with their ledgers, rowidx491: the 491 row guard's row counts), the campaign dirs' logs and found
# files (c170v, c170, c170f, c170g, c170r, c150), the CPU shares
# (c150cpu), the env and helper files in /content, vec89/made.txt and vec491/made.txt.
import os, subprocess, time, glob
os.chdir("/content")
keep = [d for d in ("c3g", "ua_v10", "ua_v3", "ua_v7", "ua_v9", "uaB", "f29fr", "f28w", "cover89", "cover491", "rowidx491", "c150cpu") if os.path.isdir(d)]
for d in ("c170v", "c170", "c170f", "c170g", "c170r", "c150"):
    for f in ("search.log", "gpu3_stats.log", "found.jsonl", "driver.log", "my_specs.json", "my_specs_pre_top2.json", "my_specs_pre_top3.json", "my_specs_pre_top4s.json", "near_events.jsonl", "kernel_discrepancy.jsonl"):
        if os.path.exists(f"{d}/{f}"):
            keep.append(f"{d}/{f}")
keep += [f for f in glob.glob("*") if os.path.isfile(f) and not f.endswith((".tgz", ".log")) and os.path.getsize(f) < 50e6]
keep += [f for f in glob.glob("*.log") if os.path.getsize(f) < 20e6 and not f.startswith("bringup")]
for f in ("vec89/made.txt", "vec491/made.txt", "vec491/seq0.txt"):
    if os.path.exists(f):
        keep.append(f)
t0 = time.time()
r = subprocess.run(["tar", "-czf", "/content/snap.tgz", "--exclude=*.so", "--exclude=__pycache__", "--exclude=walk.tmp", "--exclude=walk.part", "--exclude=chunk.tmp.json"] + keep, capture_output=True, text=True)
print("[snap]", os.popen("hostname").read().strip(), "| rc", r.returncode, r.stderr[-300:], "| size", os.path.getsize("/content/snap.tgz") // (1 << 20), "MB |", f"{time.time() - t0:.0f} s |", len(keep), "entries")
