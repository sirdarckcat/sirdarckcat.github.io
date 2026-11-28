#!/bin/bash
# 29-bit Fermat kernel (uarch 710585f), first light and speed: time_fermat28.py --check (2,000 candidates against gmpy2) and tests/s, production step against the
# 29-bit steps, on an 88-moduli spec and on an 89-moduli vector window. A separate Fermat dir /content/f29 (a copy of /content/f28w with 710585f's fermat661/cuda over
# it); production's /content/f28w untouched. Campaign paused (SIGSTOP) and resumed at the end, whatever happens.  VARIANTS / SPEC88 from the environment.
OUT=/content/t29.txt; : > $OUT
[ -d /content/f29 ] || cp -a /content/f28w /content/f29
tar -xzf /content/f29_overlay.tgz -C /content/f29
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
nvidia-smi --query-gpu=name,clocks.sm --format=csv,noheader >> $OUT
cd /content/f29
echo "--- 88 moduli: $SPEC88" >> $OUT
timeout 900 python3 time_fermat28.py $SPEC88 --variant $VARIANTS --check --seconds 20 >> $OUT 2>&1 || echo "FAILED 88" >> $OUT
echo "--- 89-moduli vector window: k in [2137898, 18915114)" >> $OUT
timeout 900 python3 time_fermat28.py /content/m89_8.json --kmin 2137898 --kmax 18915114 --variant $VARIANTS --check --seconds 20 >> $OUT 2>&1 || echo "FAILED 89" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo T29-DONE >> $OUT
