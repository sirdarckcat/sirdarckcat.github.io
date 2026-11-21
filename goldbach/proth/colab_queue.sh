#!/bin/bash
# GPU queue: 5e6 (already running) -> 1e7 -> 16,045,849. Each rung resumes from its
# tests.jsonl and is skipped if a hit is already recorded.
cd /content
echo "$(date -u +%FT%TZ) queue start" >> /content/queue.log
while pgrep -f "q5e6_spec" > /dev/null; do sleep 30; done
echo "$(date -u +%FT%TZ) 5e6 search exited" >> /content/queue.log
mkdir -p /content/q1e7
if [ ! -s /content/q1e7/hits.jsonl ]; then
  python3 gpu_search.py /content/q1e7_spec.json /content/q1e7_surv.json /content/q1e7 --batch 512 >> /content/q1e7/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) 1e7 search exited" >> /content/queue.log
until [ -f /content/q16m_surv.json ]; do sleep 60; done
mkdir -p /content/q16m
if [ ! -s /content/q16m/hits.jsonl ]; then
  python3 gpu_search.py /content/q16m_spec.json /content/q16m_surv.json /content/q16m --batch 256 >> /content/q16m/run.log 2>&1
fi
echo "$(date -u +%FT%TZ) QUEUE-DONE" >> /content/queue.log
