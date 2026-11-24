#!/bin/bash
# The T4 gate: part 1 (timing + slice identity), then part 2 (fast-path per-member identity at production f + the known case 40/40 with one-pass off).
bash /content/opl4gate1.sh > /content/opl4gate1.log 2>&1
bash /content/opl4gate2.sh > /content/opl4gate2.log 2>&1
echo T4GATE-DONE > /content/t4gate.done
