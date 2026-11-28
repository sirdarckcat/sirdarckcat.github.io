#!/bin/bash
# Deep sieve on the new GPU host's CPUs: 16M on [1e9, 1e11], then [3e11, 1e12]
# (gold-cpu covers [1e11, 3e11]; its kills arrive as q16m_surv.cpu.kills.json).
cd /content
TH=$(( $(nproc) - 2 ))
python3 deep_sieve.py q16m_spec.json q16m_surv.json 1e9 1e11 q16m_surv.json --threads $TH --every 300 > q16m_deepsieve.log 2>&1
python3 deep_sieve.py q16m_spec.json q16m_surv.json 3e11 1e12 q16m_surv.json --threads $TH --every 600 > q16m_deepsieve2.log 2>&1
echo SIEVE-CHAIN-DONE >> q16m_deepsieve2.log
