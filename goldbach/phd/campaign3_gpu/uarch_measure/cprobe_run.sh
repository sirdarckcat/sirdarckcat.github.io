#!/bin/bash
# uarch's cluster probe (c0c8ee3, lead-approved; at most 2 min paused): production paused (always resumed), probe_cluster.py, resumed.
W=/content/cprobe; P=$(pgrep -f "search_gpu5[.]py --campaign /content/c170r " | head -n 1)
[ -n "$P" ] || { echo "CPROBE: no production process" > $W/cprobe.log; exit 1; }
trap 'kill -CONT $P 2>/dev/null' EXIT
echo "CPROBE paused $P $(date -u +%T)" > $W/cprobe.log; kill -STOP $P; sleep 2
cd $W && timeout 110 python3 probe_cluster.py > $W/probe_out.txt 2>&1; echo "CPROBE probe rc=$? $(date -u +%T)" >> $W/cprobe.log
kill -CONT $P; trap - EXIT; echo "CPROBE resumed $P $(date -u +%T)" >> $W/cprobe.log; echo CPROBE-DONE >> $W/cprobe.log
