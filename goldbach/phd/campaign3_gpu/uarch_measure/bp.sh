#!/bin/bash
# uarch bench_pipes.py (38abbd2), parts 1-3 (pipes; shared memory: ATOMS.AND random / conflict-free, STS, LDS, read-modify-write at the klog 17/18/19 sizes; global
# scattered marks) on this RTX PRO 6000. A separate dir /content/bp. Campaign paused (SIGSTOP), resumed whatever happens.
OUT=/content/bp.txt; : > $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
nvidia-smi --query-gpu=name,clocks.sm,memory.used --format=csv,noheader >> $OUT
mkdir -p /content/bp && cp /content/bench_pipes_38abbd2.py /content/bp/bench_pipes.py && cd /content/bp && timeout 900 python3 bench_pipes.py >> $OUT 2>&1 || echo "FAILED rc=$?" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo BP-DONE >> $OUT
