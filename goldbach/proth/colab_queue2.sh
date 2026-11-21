#!/bin/bash
# GPU queue, restarted: 1e7 (resumes from its tests.jsonl; gpu_search now reloads
# q1e7_surv.json between batches, which deep_sieve.py keeps deepening) -> 16,045,849
# (skipping the t's the stopped CPU helper already tested).
cd /content
echo "$(date -u +%FT%TZ) queue2 start (1e7 resumed, survivors reload on)" >> /content/queue.log
mkdir -p /content/q1e7 /content/q16m
if [ ! -s /content/q1e7/hits.jsonl ]; then
  python3 gpu_search.py /content/q1e7_spec.json /content/q1e7_surv.json /content/q1e7 --batch 512 >> /content/q1e7/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) 1e7 search exited" >> /content/queue.log
if [ ! -s /content/q16m/hits.jsonl ]; then
  python3 gpu_search.py /content/q16m_spec.json /content/q16m_surv.json /content/q16m --batch 256 --done /content/q16m_cpu/tests.jsonl >> /content/q16m/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) QUEUE-DONE" >> /content/queue.log
