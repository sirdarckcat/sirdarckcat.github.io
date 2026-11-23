#!/bin/bash
# Bring up a replacement RTX PRO 6000 (G4) for a card that hit Colab's 24 h limit, on the configuration of 23 Nov ~19:30Z plus the lead's approved 491-family switch:
#   /content/snap.tgz      the old card's snapshot (snap.py): trees c3g (driver f4a85df2f2d5, top placement), ua_v10 (one-pass), ua_v3/7/9, f29fr (29-bit fused-rounds kernel),
#                          cover89 + its ledgers (kept for a 463 revert), c150cpu (CPU shares), next_campaign_env (+ _pre_onepass), deep_env_v89 (--vector-place top), scripts
#   /content/cover491.tgz  research's 491-family generator (bbc8cd8) + part.py
#   /content/vecgen491.sh, rowguard491.py, rowguard491.sh
#   bash bringup_rtx491.sh PART      (PART = the old card's generator partition: gold-g4 0, gold-g4b 1, gold-g4c 2)
# Steps: restore, install gmpy2, the production known case on this GPU (kc_prod.sh: 23/23 or stop), the 491 generator for PART (vec491), the campaign in a fresh dir
# (c170r, vector mode, production's env and deep_env_v89), the 491 row guard (base after 2,000 vectors). Log: /content/bringup.log
PART=${1:?partition}
L=/content/bringup.log
echo "$(date -u +%FT%TZ) bring-up start, partition $PART, $(hostname), $(nvidia-smi --query-gpu=name --format=csv,noheader)" >> $L
cd /content && tar -xzf /content/snap.tgz >> $L 2>&1 || { echo "BRINGUP-FAILED restore" >> $L; exit 1; }
python3 -c 'import gmpy2' 2>/dev/null || pip install -q gmpy2 >> $L 2>&1
python3 -c 'import gmpy2, cupy; print("gmpy2", gmpy2.version(), "cupy", cupy.__version__)' >> $L 2>&1
mkdir -p /content/cover491 && tar -xzf /content/cover491.tgz -C /content/cover491 && (cd /content/cover491 && gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm) >> $L 2>&1 \
  || { echo "BRINGUP-FAILED covergen" >> $L; exit 1; }
bash /content/kc_prod.sh >> $L 2>&1
grep -h "KCPROD\|known case" /content/kc_prod/result.txt >> $L
grep -q "KCPROD PASSED" /content/kc_prod/result.txt || { echo "BRINGUP-FAILED known case on this GPU" >> $L; exit 1; }
mkdir -p /content/vec491 /content/c170r
setsid nohup bash /content/vecgen491.sh /content/vec491 /content/c170r $PART 3 >> /content/vecgen491.log 2>&1 < /dev/null &
for i in $(seq 1 120); do ls /content/vec491/vec_*.json > /dev/null 2>&1 && break; sleep 5; done
ls /content/vec491/vec_*.json > /dev/null 2>&1 || { echo "BRINGUP-FAILED no 491 chunk after 10 min: $(tail -n 2 /content/vecgen491.log)" >> $L; exit 1; }
echo "$(date -u +%FT%TZ) first 491 chunk: $(tail -n 1 /content/vecgen491.log | cut -c1-220)" >> $L
setsid nohup bash -c 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" bash /content/run_v5_vec.sh /content/c170r /content/vec491' > /dev/null 2>&1 < /dev/null &
setsid nohup bash /content/rowguard491.sh > /dev/null 2>&1 < /dev/null &
sleep 60
echo "$(date -u +%FT%TZ) campaign procs $(pgrep -fc 'search_gpu5[.]py --campaign /content/c170r ') | $(tail -n 1 /content/c170r/search.log 2>/dev/null | cut -c1-200)" >> $L
echo BRINGUP-DONE >> $L
