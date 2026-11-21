#!/bin/bash
# Deep sieve on the A100 host's CPUs (10 threads): 1e7 to 1e11 (abandoned if the
# 1e7 rung hits first), then 16M to 1e11, then 16M on to 1e12.
cd /content
python3 deep_sieve.py q1e7_spec.json q1e7_surv.json 1e9 1e11 q1e7_surv.json --threads 10 --every 300 > q1e7_deepsieve.log 2>&1 &
pid=$!
while kill -0 $pid 2>/dev/null; do
  if [ -s /content/q1e7/hits.jsonl ]; then pkill -f "deepsieve /content/.deepsieve"; kill $pid; echo "abandoned: 1e7 hit" >> q1e7_deepsieve.log; break; fi
  sleep 10
done
python3 deep_sieve.py q16m_spec.json q16m_surv.json 1e9 1e11 q16m_surv.json --threads 10 --every 300 > q16m_deepsieve.log 2>&1
python3 deep_sieve.py q16m_spec.json q16m_surv.json 1e11 1e12 q16m_surv.json --threads 10 --every 600 > q16m_deepsieve2.log 2>&1
echo SIEVE-CHAIN-DONE >> q16m_deepsieve2.log
