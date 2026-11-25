#!/bin/bash
# The lead's item 1 (carry-over), identity gate on this RTX card (25 Nov): production paused (always resumed), three runs in scratch dirs:
#   A: the production engine (/content/c3g/search_gpu5.py, fround /content/f29fr) on 28 vectors this card has done, production options, --near-miss 50000 --profile-pool 1;
#   B: the carry-over engine (search_gpu5_carry.py = 9385f3b + uarch fe27cbe + --record, fround_carry.py) on the same vectors, --carry-over 1 --near-miss 50000 --record 160357;
#   C: the production known case (q170000_m89_t1_v0, 2^19 window, f = 0, near-misses >= 46,171) with the carry-over engine: the CPU brute force's 23 (k, q).
W=/content/cgate; rm -rf $W/runA $W/runB $W/runC $W/vec $W/vecC $W/f29c; mkdir -p $W/runA $W/runB $W/runC $W/vec $W/vecC
cp $W/search_gpu5_carry.py /content/c3g/search_gpu5_carry.py
cp -r /content/f29fr $W/f29c; cp $W/fround_carry.py $W/f29c/fround.py
P=$(pgrep -f "search_gpu5[.]py --campaign /content/c170r " | head -n 1)
[ -n "$P" ] || { echo "CGATE: no production process" > $W/cgate.log; exit 1; }
CMD=$(tr '\0' ' ' < /proc/$P/cmdline); ENVS=$(tr '\0' '\n' < /proc/$P/environ | grep -E '^(DEEP_|GBATCH_|SIEVE200=|K28_)' | grep -v '^DEEP_ARGS=' | tr '\n' ' ')
ARGS=$(echo "$CMD" | sed -e 's#^python3 /content/c3g/search_gpu5.py ##' -e 's#--campaign [^ ]*##' -e 's#--vector-dir [^ ]*##' -e 's#--near-miss [0-9]*##')
python3 - <<'PY'
import glob, json, re
done = set()
for l in open("/content/c170r/search.log"):
    m = re.match(r"\[(\S+)@\d+\] k=\[", l)
    if m: done.add(m.group(1))
for f in sorted(glob.glob("/content/vec491/vec_*.json")):
    specs = [s for s in json.load(open(f)) if s["name"] in done]
    if len(specs) >= 28:
        json.dump(specs[:28], open("/content/cgate/vec/vec_000000.json", "w")); print("CGATE vectors: 28 done from", f, specs[0]["name"], "..", specs[27]["name"]); break
else:
    raise SystemExit("CGATE: no chunk with 28 done vectors")
s = json.load(open("/content/m89_8.json")); json.dump(s[:1], open("/content/cgate/vecC/vec_000000.json", "w"))
PY
[ -s $W/vec/vec_000000.json ] && [ -s $W/vecC/vec_000000.json ] || exit 1
echo "CGATE production pid $P: $CMD" > $W/cgate.log
trap 'kill -CONT $P 2>/dev/null' EXIT
kill -STOP $P; echo "CGATE paused $P $(date -u +%T)" >> $W/cgate.log
( export $ENVS; export FERMAT28_DIR=/content/f29fr
  timeout 400 python3 /content/c3g/search_gpu5.py --campaign $W/runA --vector-dir $W/vec --vector-wait 3 $ARGS --near-miss 50000 --profile-pool 1 > $W/runA/driver.log 2>&1 )
echo "CGATE run A rc=$? $(date -u +%T)" >> $W/cgate.log
( export $ENVS; export FERMAT28_DIR=$W/f29c
  timeout 400 python3 /content/c3g/search_gpu5_carry.py --campaign $W/runB --vector-dir $W/vec --vector-wait 3 $ARGS --near-miss 50000 --record 160357 --carry-over 1 --profile-pool 1 > $W/runB/driver.log 2>&1 )
echo "CGATE run B rc=$? $(date -u +%T)" >> $W/cgate.log
( export $ENVS; export FERMAT28_DIR=$W/f29c
  timeout 400 python3 /content/c3g/search_gpu5_carry.py --campaign $W/runC --vector-dir $W/vecC --vector-wait 3 $ARGS --batch 1 --skip-frac 0 --near-miss 46171 --klog 19 --slice 524288 --pipeline-depth 1 --vector-place bottom --carry-over 1 > $W/runC/driver.log 2>&1 )
echo "CGATE run C rc=$? $(date -u +%T)" >> $W/cgate.log
kill -CONT $P; trap - EXIT; echo "CGATE resumed $P $(date -u +%T)" >> $W/cgate.log
python3 $W/cmp_cgate.py >> $W/cgate.log 2>&1
echo CGATE-DONE >> $W/cgate.log
