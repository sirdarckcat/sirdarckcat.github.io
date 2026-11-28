#!/bin/bash
# GPU queue on the new runtime: resume 1e7 from its tests.jsonl (deep-sieved list), then 16,045,849.
cd /content
echo "$(date -u +%FT%TZ) queue3 start on $(nvidia-smi --query-gpu=name --format=csv,noheader)" >> /content/queue.log
mkdir -p /content/q1e7 /content/q16m
if [ ! -s /content/q1e7/hits.jsonl ]; then
  python3 gpu_search.py /content/q1e7_spec.json /content/q1e7_surv.json /content/q1e7 --batch 512 >> /content/q1e7/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) 1e7 search exited" >> /content/queue.log
if [ ! -s /content/q16m/hits.jsonl ]; then
  python3 gpu_search.py /content/q16m_spec.json /content/q16m_surv.json /content/q16m --batch 256 --done /content/q16m_cpu/tests.jsonl >> /content/q16m/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) QUEUE-DONE" >> /content/queue.log
