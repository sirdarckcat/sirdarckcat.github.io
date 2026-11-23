#!/bin/bash
# vtop.sh's normal-path check again with the normal path's own window (2^19: --klog 20 cannot set the GPU sieve kernel's shared memory, CUDA_ERROR_INVALID_VALUE):
# --vector-place top --klog 19 on the same production vector (vtop/vn), f = 0.97 / 0.9 (dirs nb97 / nb90), then search_c.py on the same k range [kend - 2^19, kend) (cb97 / cb90).
# Runs after vtop.sh has exited; the campaign is paused (SIGSTOP) for the two GPU runs only.
W=/content/vtop; cd $W
for i in $(seq 1 900); do pgrep -f 'bash /content/vtop[.]sh' > /dev/null || break; sleep 2; done
rm -rf nb97 nb90 cb97 cb90 result2.txt
E=$(cat /content/next_campaign_env); G=/content/c3g; NEW=$G/search_gpu5_vtop.py
python3 - <<'PY'
import json
from gmpy2 import mpz
s = json.load(open("/content/vtop/vn/vec_000000.json"))[0]
N0, M = mpz(s["N0"]), mpz(s["M"]); kend = min(int(s["kmax"]), int((mpz(10) ** 200 - N0 + M - 1) // M)); ks = kend - (1 << 19)
json.dump([dict(s, name=f"{s['name']}@{ks}", kstart=ks, kmax=kend)], open("/content/vtop/slice_top19.json", "w"))
print(f"normal-path vector {s['name']}: top 2^19 = [{ks}, {kend})")
PY
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status2.txt
for f in 97 90; do
  D=$W/nb$f; mkdir -p $D
  ( export $E
    timeout 600 python3 $NEW --campaign $D --vector-dir $W/vn --vector-wait 3 --vector-place top --klog 19 --goldbach $G --batch 1 --pool 2097152 --skip-frac 0.$f --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --sieve-b 1000000 --block 32768 --fused-rounds 1 \
      > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
done
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status2.txt
CG=/content/c150cpu/goldbach
for f in 97 90; do
  D=$W/cb$f; mkdir -p $D
  timeout 3000 nice -n 5 python3 $CG/sieve200/search_c.py $W/slice_top19.json --procs 8 --block 32768 --sieve-b 1000000 --skip-frac 0.$f --p-est 0.055 --out $D/found.jsonl > $D/out.txt 2>&1
  echo "rc=$?" >> $D/out.txt
done
echo "$(date -u +%FT%TZ) CPU slices done" >> status2.txt
python3 - <<'PY' > result2.txt 2>&1
import os, re
W = "/content/vtop"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def sl(f):
    return {m.group(1): (int(m.group(2)), int(m.group(3)), m.group(4)) for m in map(pat.match, rd(f)) if m}
def errs(f):
    return [l.strip()[:160] for l in rd(f) if "rror" in l or "Traceback" in l or "outside" in l or "ssert" in l][:3]
print(open(f"{W}/status2.txt").read().strip())
ok = True
for f in ("97", "90"):
    g, c = sl(f"{W}/nb{f}/search.log"), sl(f"{W}/cb{f}/out.txt")
    same = bool(g) and g == c and not errs(f"{W}/nb{f}/driver.log"); ok = ok and same
    print(f"normal path, top 2^19, f = 0.{f}: GPU {g} | CPU {c} | {'IDENTICAL' if same else 'DIFFERENT'} | {errs(W + '/nb' + f + '/driver.log')} {errs(W + '/cb' + f + '/out.txt')}")
print("VTOP-NORMAL", "PASSED" if ok else "FAILED")
print("VTOP2-DONE")
PY
