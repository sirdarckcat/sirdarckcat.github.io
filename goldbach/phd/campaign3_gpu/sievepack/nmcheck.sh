#!/bin/bash
# Per-member check of the one-pass kernel's FAST path at production's window (2^24, 32 tiles x rcta 8 = 256 bins, ~24 marks a bin < 40 slots): the known case's 2^19 window has one tile
# (8 bins, ~768 marks a bin), so there every CTA takes the fallback path. Here: the known-case vector (q170000_m89_t1_v0), its top 2^24 window (production placement), f = 0 (every
# member tested), near-misses >= 46,171 (row 400): the list of (k, first-PRP row) with the settings before one-pass (next_campaign_env_pre_onepass: tree and options) against the
# current ones (ua_v10 + ONEPASS): must be identical, and the slice lines too. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/nmcheck; rm -rf $W; mkdir -p $W/vec; cd $W
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$W/vec/vec_000000.json', 'w'))"
EO=$(cat /content/next_campaign_env_pre_onepass); EN=$(cat /content/next_campaign_env)
DA=$(cat /content/deep_env_v89 | sed -e 's/--pipeline-depth [0-9]*//'); 
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name env
  D=$W/$1; mkdir -p $D
  ( export $2
    timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $W/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 $DA --pipeline-depth 1 > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
}
run old "$EO"; run new "$EN"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/nmcheck"
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def nms(d):
    return sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in rd(f"{W}/{d}/found.jsonl") if t.strip()))
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    return {m.group(1): (m.group(2), m.group(3), m.group(4)) for m in map(pat.match, rd(f"{W}/{d}/search.log")) if m}
a, b = nms("old"), nms("new")
print(open(f"{W}/status.txt").read().strip())
print("old env:", [e for e in open("/content/next_campaign_env_pre_onepass").read().split() if e.startswith(("SIEVE200", "DEEP_GEN"))])
print("new env:", [e for e in open("/content/next_campaign_env").read().split() if e.startswith(("SIEVE200", "DEEP_GEN"))])
print("old slice:", sl("old")); print("new slice:", sl("new"))
print(f"near-misses >= 46,171: old {len(a)}, new {len(b)}, identical {a == b}; only old {sorted(set(a) - set(b))[:5]}, only new {sorted(set(b) - set(a))[:5]}")
print("errors:", [l[:150] for d in ("old", "new") for l in rd(f"{W}/{d}/driver.log") if "rror" in l or "Traceback" in l][:3])
print("NMCHECK", "PASSED" if a == b and a and sl("old") == sl("new") and sl("old") else "FAILED")
PY
