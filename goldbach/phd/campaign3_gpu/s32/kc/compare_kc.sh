#!/bin/bash
# The shift gate's point 2: the GPU's near-misses on the shifted known-case vector (f = 0, 2^19 window at the top, T = 48,397) against cpu_brute_k0.py's.
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
G=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/tasks/bx06vecbm.output
grep '^GPU k=' $G | sed 's/^GPU //' | sort > $SP/s32/kc/gpu_pairs.txt
grep '^BRUTE k=' $SP/s32/kc/kc_s32_cpu_brute.txt | sed 's/^BRUTE //' | sort > $SP/s32/kc/cpu_pairs.txt
g=$(wc -l < $SP/s32/kc/gpu_pairs.txt); c=$(wc -l < $SP/s32/kc/cpu_pairs.txt)
if cmp -s $SP/s32/kc/gpu_pairs.txt $SP/s32/kc/cpu_pairs.txt && [ "$g" -gt 0 ]; then echo "S32-KC PASSED: GPU $g = CPU $c (k, q) pairs, identical"; else echo "S32-KC FAILED: GPU $g, CPU $c"; diff $SP/s32/kc/gpu_pairs.txt $SP/s32/kc/cpu_pairs.txt | head -n 20; fi
