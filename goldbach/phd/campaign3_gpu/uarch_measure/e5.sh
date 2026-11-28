#!/bin/bash
# uarch bench_fm28_step.py --e5 (02b90fc): dummy FFMA / IADD3 / IMAD.WIDE inside the real Fermat step (does the FP32 pipe run beside IMAD.WIDE?) on this RTX PRO 6000.
# A separate Fermat dir /content/fe5 (a copy of /content/f29 with 02b90fc's bench_fm28_step.py and gen_fermat28.py); production's dirs untouched. Campaign paused, resumed whatever happens.
OUT=/content/e5.txt; : > $OUT
[ -d /content/fe5 ] || cp -a /content/f29 /content/fe5
tar -xzf /content/e5_overlay.tgz -C /content/fe5
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
nvidia-smi --query-gpu=name,clocks.sm --format=csv,noheader >> $OUT
cd /content/fe5 && timeout 600 python3 bench_fm28_step.py --e5 >> $OUT 2>&1 || echo "FAILED rc=$?" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo E5-DONE >> $OUT
