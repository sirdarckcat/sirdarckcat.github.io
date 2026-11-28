#!/bin/bash
# profile.sh [slice] [cpu]     default slice 7/400 (about 1 minute), cpu 2
# Statistical profile of fscan on this machine: builds fscan with -g -no-pie (same code generation as a normal -O3 build), runs one
# class-194 slice on one thread under sampler.c (10 kHz), and prints the share of the samples by source line and by stage.
# Needs gcc, addr2line (binutils), setarch (util-linux), python3.  Run it on an otherwise idle core.  Nothing is written outside /tmp.
SLICE=${1:-7/400}; CPU=${2:-2}
HERE=$(cd "$(dirname "$0")" && pwd); cd "$HERE/.."
T=$(mktemp -d /tmp/profile.XXXXXX)
gcc -O3 -g -no-pie -march=native -fopenmp -Wno-unused-result -o $T/fscan fscan.c -lm || exit 1
gcc -O2 -shared -fPIC -o $T/libsampler.so profile/sampler.c -lrt || exit 1
RUN=""; command -v taskset >/dev/null && RUN="taskset -c $CPU"
echo "== $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2) =="
SAMPLER_OUT=$T/samples.txt LD_PRELOAD=$T/libsampler.so $RUN setarch -R $T/fscan 10007 383 194 194 4e18 1e23 99 113 slice=$SLICE threads=1 2>&1 | grep -E "STATS" | sed 's/STATS Q=.*| vectors/STATS vectors/' | cut -c1-150
python3 profile/report.py $T/samples.txt $T/fscan fscan.c ${TOP:-40}
rm -rf $T
